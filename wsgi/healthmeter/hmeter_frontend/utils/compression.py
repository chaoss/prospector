# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import cStringIO
import zlib
import bz2
import logging
import magic

from .filetools import ChainFile

logger = logging.getLogger(__name__)


class DecompressorFileProxy(object):
    """
    Helper class that provides a file-like interface to reading decompressed
    data from another file object. This class is the base class that provides
    functionality common to the specialized DecompresorFileProxy classes.
    """

    buffer_ = cStringIO.StringIO('')

    def _read(self):
        """
        Read more data from the decompressor

        @return Data from the decompressor
        """
        return ''

    def read(self, size=-1):
        """
        Read decompressed data up to `size' in length. Data is read from
        self._read() and buffered internally if it exceeds `size'.

        @arg size Upper limit on length of data to read. -1 for no limit.
        @return data no longer than `size'
        """

        retval = cStringIO.StringIO()

        if size < 0:
            retval.write(self.buffer_.read())

        else:
            retval.write(self.buffer_.read(size))

        while size < 0 or retval.tell() < size:
            moredata = self._read()
            if not moredata:
                break

            if size >= 0 and len(moredata) + retval.tell() > size:
                # Overflow, slice it up and store remaining in the buffer
                remsize = size - retval.tell()
                retval.write(moredata[:remsize])
                self.buffer_ = cStringIO.StringIO(moredata[remsize:])

            else:
                retval.write(moredata)

        return retval.getvalue()


class GZDecompressorFileProxy(DecompressorFileProxy):
    """ Specialization of DecompressorFileProxy that handles gz streams"""

    def __init__(self, fileobj, chunksize=4096):
        self.fileobj = fileobj
        # See http://stackoverflow.com/questions/2423866/
        self.decompressor = zlib.decompressobj(15 + 32)
        self.chunksize = 4096

    def _read(self):
        return self.decompressor.decompress(self.fileobj.read(self.chunksize))


class BZ2DecompressorFileProxy(DecompressorFileProxy):
    """Specialization of DecompressorFileProxy that handles bz2 streams"""

    def _init__(self, fileobj, chunksize=4096):
        self.fileobj = fileobj
        self.decompressor = bz2.BZ2Decompressor()
        self.chunksize = self.chunksize

    def _read(self):
        try:
            return self.decompressor.decompress(
                self.fileobj.read(self.chunksize))

        except EOFError:
            return ''


def get_decompressed_fileobj(fileobj):
    """
    Constructs a suitable DecompressorFileProxy for fileobj by parsing the
    compression method out of the extension found in filename.

    @arg fileobj    File-like object to use as input
    @return DecompressorFileProxy instance
    """
    available_decompressors = {
        'application/x-gzip': GZDecompressorFileProxy,
        'application/x-bzip2': BZ2DecompressorFileProxy
    }

    m = magic.Magic(mime=True)
    buf = fileobj.read(100)
    fileobj = ChainFile(cStringIO.StringIO(buf),
                        fileobj)

    try:
        return available_decompressors[m.from_buffer(buf)](fileobj)

    except KeyError, e:
        logger.warn("Could not find compressor for [%s], returning "
                    "original fileobj", e.args[0])
        return fileobj


__all__ = [
    'DecompressorFileProxy',
    'GZDecompressorFileProxy',
    'BZ2DecompressorFileProxy',
    'get_decompressed_fileobj'
]
