# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

"""
CVE importer module. This module doesn't share the same interface as the other
importers due to the specificity of this particular bit of data. There are no
different "types", and since the CVEs come in huge XML files, it's best to
process everything in one run rather than on a project-by-project basis.
"""
import bs4
import calendar
import errno
import filecmp
import httplib
import iso8601
import logging
import lxml.etree
import os
import re
import requests
import rfc822
import shutil
import time
import urllib2

from django.db import transaction, IntegrityError
from healthmeter.cveinfo.models import CVE, Product
from healthmeter.importerutils.importers import ImporterBase
from healthmeter import utils

logger = logging.getLogger(__name__)


class CVEImporter(ImporterBase):
    model = Product

    @classmethod
    def resolve_importer_type(cls, cpe):
        return 'cve'

    @staticmethod
    def get_cve_links():
        """Returns an iterable of links to CVE dump files"""
        response = urllib2.urlopen('https://nvd.nist.gov/download.cfm')
        parser = bs4.BeautifulSoup(response)
        links = parser.findAll('a')

        response.close()

        cve_regex = re.compile(r'^https://.*nvdcve-2.0-[0-9]{4}.xml$')

        return (link['href'] for link in links
                if cve_regex.match(link.get('href', '')))

    @staticmethod
    def download_cvedb():
        basedir = os.path.join(os.getenv('OPENSHIFT_DATA_DIR',
                                         os.getenv('TMPDIR', '/tmp')),
                               'cves')
        try:
            os.makedirs(basedir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        files = []

        logger.info("Scraping NIST for CVE dump files")

        for link in CVEImporter.get_cve_links():
            filename = os.path.join(basedir, os.path.basename(link))
            files.append(filename)

            logger.info("Found %s at %s", filename, link)

            def check_file_needs_renewal(filename):
                try:
                    return (os.stat(filename).st_mtime -
                            time.time() > 3600 * 24 * 2)

                except OSError:
                    return True

            # If mtime is more than 2 days ago, refresh the file
            while check_file_needs_renewal(filename):
                tmpfilename = filename + '.new'

                # Open file exclusively to avoid races
                try:
                    fd = os.open(tmpfilename,
                                 os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                except OSError, e:
                    if e.errno != errno.EEXIST:
                        logger.error("Could not open %s for writing.",
                                     tmpfilename,
                                     exc_info=True)
                        raise

                    fd = None

                if fd is not None:
                    # Successfully opened, so make a fileobj to write to
                    try:
                        with os.fdopen(fd, "w") as f:
                            logger.info("Successfully opened %s for writing."
                                        "Starting download...", tmpfilename)
                            response = requests.get(link, stream=True)

                            for chunk in response.iter_content(
                                    chunk_size=4096):
                                if not chunk:
                                    break

                                f.write(chunk)

                        os.rename(tmpfilename, filename)

                        # We're done here, so break out of the mtime check loop
                        break

                    except Exception, e:
                        # Make sure that tmpfilename is deleted if we failed
                        # for some reason.
                        logger.warn("Failed to download tmp file! Deleting...",
                                    exc_info=True)
                        try:
                            os.unlink(tmpfilename)
                        except OSError:
                            pass

                        raise e

                else:
                    # someone else has opened the .tmp file
                    time.sleep(60)

        return files

    xml_namespaces = {
        'default': "http://scap.nist.gov/schema/feed/vulnerability/2.0",
        'vuln': "http://scap.nist.gov/schema/vulnerability/0.4",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'cpe-lang': "http://cpe.mitre.org/language/2.0",
        'patch': "http://scap.nist.gov/schema/patch/0.1",
        'scap-core': "http://scap.nist.gov/schema/scap-core/0.1",
        'cvss': "http://scap.nist.gov/schema/cvss-v2/0.2",

        're': 'http://exslt.org/regular-expressions'
    }

    date_xpath = lxml.etree.XPath("./vuln:published-datetime",
                                  namespaces=xml_namespaces)

    def __init__(self, *args, **kwargs):
        super(CVEImporter, self).__init__(*args, **kwargs)

        product_xpath_regex = (
            r'^cpe:(2.3:|/)[aoh]?:({vendor}:{product})(:|$)'.format(
                vendor=self.object.vendor,
                product=self.object.product))

        self.entries_xpath = lxml.etree.XPath(
            "/default:nvd/default:entry[re:test("
            "vuln:vulnerable-software-list/vuln:product, '" +
            product_xpath_regex + "', 'i')]", namespaces=self.xml_namespaces)

        logger.debug('Entries xpath is [%s]', self.entries_xpath.path)

    @transaction.atomic
    def _run(self):
        logger.info("Importing CVEs for [%s]", self.object)
        files = self.download_cvedb()

        for fname in files:
            try:
                with open(fname, 'r') as f:
                    self.parse_file(f)
            except:
                logger.error("Could not parse [%s]. Skipping...", fname,
                             exc_info=True)

    def parse_file(self, fileobj):
        """
        Parse CVEs

        @arg fileobj File-like object to XML interface to parse for CVE
                     information
        @arg products_index Dict of `vendor:product' products
        """
        parse_tree = lxml.etree.parse(fileobj)

        # cve to extract date and number from CVE ID
        cve_regex = re.compile(r'CVE-(?P<year>\d{4})-(?P<number>\d{4,})')

        for entry in self.entries_xpath(parse_tree):
            cve_id = entry.attrib['id']
            cveinfo = cve_regex.match(cve_id)

            date = iso8601.parse_date(self.date_xpath(entry)[0].text) \
                .astimezone(iso8601.iso8601.UTC) \
                .replace(tzinfo=None)

            cve, created = self.object.cves.get_or_create(
                year=cveinfo.group('year'),
                number=cveinfo.group('number'),
                defaults={'published_datetime': date})

            logger.info('%s [%s]',
                        'Imported' if created else 'Got',
                        cve_id)

            # Update CVE published_datetime
            if not created and cve.published_datetime != date:
                logger.info('Updating published_datetime of [%s] from [%s] to '
                            '[%s]',
                            cve_id, cve.published_datetime, date)
                cve.published_datetime = date
                cve.save()
                self.record_timestamp(date)

            elif created:
                self.record_timestamp(date)


CVEImporter.register_importer('cve', CVEImporter)
