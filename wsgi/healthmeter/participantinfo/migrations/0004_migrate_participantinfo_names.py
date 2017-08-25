# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models, connection, transaction, IntegrityError
import operator
from itertools import chain, imap, ifilter, groupby

class Migration(DataMigration):
    """
    Normalize the Participant and EmailAddress tables by factoring out all the
    different participant names into their own ParticipantName entries.
    """

    depends_on = (
        ('vcsinfo', '0001_initial.py'),
        ('mlinfo', '0001_initial.py'),
        ('btinfo', '0001_initial.py'),
        ('ircinfo', '0001_initial.py'),
        ('bloginfo', '0001_initial.py')
    )

    def forwards(self, orm):
        EmailAddress = orm['participantinfo.emailaddress']
        ParticipantName = orm['participantinfo.participantname']
        Participant = orm['participantinfo.participant']

        GroupedParticipants = self._group_participants(orm)
        self._combine_participants(orm, GroupedParticipants)

    def _group_participants(self, orm):
        """
        Yields an iterable of groups of duplicate participants
        """
        Participant = orm['participantinfo.Participant']

        db.execute("""
            CREATE TEMP TABLE participantinfo_grouped_participants
            ON COMMIT DROP AS
            SELECT DISTINCT ON (pe.owner_id)
                   pe.owner_id AS participant_id,
                   (SELECT MIN(pe2.owner_id)
                    FROM participantinfo_emailaddress pe2
                    WHERE (pe2.localpart, pe2.domainpart_id) IN
                          (SELECT pe3.localpart, pe3.domainpart_id
                           FROM participantinfo_emailaddress pe3
                           WHERE pe3.owner_id = pe.owner_id))
                    AS main_participant_id
            FROM participantinfo_emailaddress pe
            WHERE NOT (pe.localpart = '' AND pe.domainpart_id IS NULL);

            DELETE FROM participantinfo_grouped_participants
            WHERE main_participant_id IS NULL;

            CREATE INDEX ON
            participantinfo_grouped_participants (participant_id);

            CREATE UNIQUE INDEX ON participantinfo_grouped_participants
            (participant_id, main_participant_id);

            ANALYZE participantinfo_grouped_participants;
            """)

        class GroupedParticipants(models.Model):
            participant = models.ForeignKey(Participant,
                                            related_name='gp')
            main_participant = models.ForeignKey(Participant)

            class Meta:
                db_table = 'participantinfo_grouped_participants'

        return GroupedParticipants

    def _combine_participants(self, orm, GroupedParticipants):
        Participant = orm['participantinfo.participant']
        ParticipantName = orm['participantinfo.participantname']
        EmailAddress = orm['participantinfo.emailaddress']

        related_objects = ifilter(
            lambda relobj: relobj.model is not EmailAddress,
            chain(
                Participant._meta.get_all_related_objects(),
                Participant._meta.get_all_related_many_to_many_objects()))

        # migrate all related objects that aren't EmailAddress
        for relo in related_objects:
            db.execute(
                """
                UPDATE {tbl} relotbl
                SET {col} = (SELECT main_participant_id
                             FROM participantinfo_grouped_participants pgp
                             WHERE pgp.participant_id = relotbl.{col})
                WHERE EXISTS (SELECT 1
                              FROM participantinfo_grouped_participants pgp2
                              WHERE pgp2.participant_id = relotbl.{col});
                """.format (tbl=relo.model._meta.db_table,
                            col=relo.field.column)
            )

        # migrate emails
        db.execute(
            """
            UPDATE participantinfo_emailaddress pe
            SET owner_id = (
                SELECT pgp.main_participant_id
                FROM participantinfo_grouped_participants pgp
                WHERE pgp.participant_id = pe.owner_id
            )
            WHERE NOT EXISTS (
                SELECT 1
                FROM participantinfo_emailaddress pe2,
                     participantinfo_grouped_participants pgp
                WHERE pgp.participant_id = pe.owner_id
                AND pe2.localpart = pe.localpart
                AND (pe2.domainpart_id = pe.domainpart_id OR
                     pe2.domainpart_id IS NULL AND pe.domainpart_id IS NULL)
                AND pe2.owner_id = pgp.main_participant_id
            )
            AND NOT (pe.localpart = '' AND pe.domainpart_id IS NULL)
            AND EXISTS (
                SELECT 1 FROM participantinfo_grouped_participants pgp2
                WHERE pgp2.participant_id = pe.owner_id
            );
            """)

        # migrate names
        db.execute("""
        INSERT INTO participantinfo_participantname (name, participant_id)
        SELECT DISTINCT
            p.name AS name,
            gp.main_participant_id AS participant_id
        FROM participantinfo_participant p
        INNER JOIN participantinfo_grouped_participants gp
        ON p.id = gp.participant_id
        WHERE NOT EXISTS (
            SELECT 1 FROM participantinfo_participantname pn
            WHERE pn.participant_id = gp.main_participant_id
            AND pn.name = p.name
        );
        """)

        # delete the rest of the participants
        Participant.objects.filter(
            id__in=GroupedParticipants.objects.exclude(
                participant=models.F('main_participant')) \
                                  .values('participant')) \
                            .delete()

    def backwards(self, orm):
        EmailAddress = orm['participantinfo.emailaddress']
        ParticipantName = orm['participantinfo.participantname']
        Participant = orm['participantinfo.participant']

        # Get list of names that don't match participant.name
        names = ParticipantName.objects \
                               .exclude(name=models.F('participant__name')) \
                               .select_related('participant')

        for name in names.iterator():
            part = name.participant
            emails = list(part.email_addresses.all().iterator())

            newpart_query = models.Q(name=name.name) & reduce(
                operator.or_,
                (models.Q(email_addresses__localpart=e.localpart,
                          email_addresses__domainpart=e.domainpart)
                 for e in emails))

            # obtain the participant for this name.
            try:
                newpart = Participant.objects.filter(newpart_query)[:1][0]
            except IndexError:
                newpart = Participant.objects.create(name=name.name)

            # copy all emails over
            for email in emails:
                newpart.email_addresses.get_or_create(
                    localpart=email.localpart,
                    domainpart=email.domainpart)

    models = {
        u'bloginfo.blog': {
            'Meta': {'object_name': 'Blog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'related_name': "'blogs'", 'blank': 'True', 'to': u"orm['projectinfo.Project']"}),
            'rss_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '255'})
        },
        u'bloginfo.post': {
            'Meta': {'unique_together': "(('blog', 'guid'),)", 'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['participantinfo.Participant']", 'null': 'True'}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': u"orm['bloginfo.Blog']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'})
        },
        u'btinfo.bug': {
            'Meta': {'unique_together': "(('tracker_info', 'bug_id'),)", 'object_name': 'Bug'},
            'bug_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'severity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'null': 'True', 'to': u"orm['btinfo.Severity']"}),
            'tracker_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': u"orm['btinfo.BugNamespace']"})
        },
        u'btinfo.bugnamespace': {
            'Meta': {'unique_together': "(('product', 'component', 'bug_tracker'),)", 'object_name': 'BugNamespace'},
            'bug_tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'namespaces'", 'to': u"orm['btinfo.BugTracker']"}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'related_name': "'bug_trackers'", 'blank': 'True', 'to': u"orm['projectinfo.Project']"})
        },
        u'btinfo.bugtracker': {
            'Meta': {'object_name': 'BugTracker'},
            'baseurl': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'bt_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['btinfo.Type']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('healthmeter.fields.PlaintextPasswordField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'btinfo.comment': {
            'Meta': {'unique_together': "(('bug', 'comment_id'),)", 'object_name': 'Comment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bug_comments'", 'to': u"orm['participantinfo.Participant']"}),
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['btinfo.Bug']"}),
            'comment_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'btinfo.severity': {
            'Meta': {'object_name': 'Severity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'btinfo.type': {
            'Meta': {'object_name': 'Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        u'ircinfo.channel': {
            'Meta': {'ordering': "('server__name', 'name')", 'unique_together': "(('server', 'name'),)", 'object_name': 'Channel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'meeting_logs_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'related_name': "'irc_channels'", 'blank': 'True', 'to': u"orm['projectinfo.Project']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'channels'", 'to': u"orm['ircinfo.Server']"})
        },
        u'ircinfo.meeting': {
            'Meta': {'ordering': "['time_start']", 'unique_together': "(('channel', 'time_start'),)", 'object_name': 'Meeting'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meetings'", 'to': u"orm['ircinfo.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ircinfo.message': {
            'Meta': {'object_name': 'Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ircinfo.User']"}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['ircinfo.Channel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ircinfo.server': {
            'Meta': {'object_name': 'Server'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'ircinfo.user': {
            'Meta': {'unique_together': "(('nickname', 'server'),)", 'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'irc_logins'", 'to': u"orm['participantinfo.Participant']"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ircinfo.Server']"})
        },
        u'mlinfo.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'archive_url': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'posting_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'projects': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'related_name': "'mailing_lists'", 'blank': 'True', 'through': u"orm['mlinfo.MailingListProject']", 'to': u"orm['projectinfo.Project']"})
        },
        u'mlinfo.mailinglistproject': {
            'Meta': {'ordering': "('project__name',)", 'unique_together': "(('project', 'mailing_list'),)", 'object_name': 'MailingListProject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mlinfo.MailingList']"}),
            'project': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['projectinfo.Project']"}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mlinfo.Purpose']"})
        },
        u'mlinfo.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mailing_list_posts'", 'to': u"orm['participantinfo.Participant']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailing_lists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'posts'", 'symmetrical': 'False', 'to': u"orm['mlinfo.MailingList']"}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_rel_+'", 'to': u"orm['mlinfo.Post']"}),
            'subject': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'mlinfo.purpose': {
            'Meta': {'object_name': 'Purpose'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'participantinfo.emailaddress': {
            'Meta': {'unique_together': "(('owner', 'localpart', 'domainpart'),)", 'object_name': 'EmailAddress'},
            'domainpart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'null': 'True', 'to': u"orm['participantinfo.EmailDomain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localpart': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_addresses'", 'to': u"orm['participantinfo.Participant']"})
        },
        u'participantinfo.emaildomain': {
            'Meta': {'ordering': "['domain']", 'object_name': 'EmailDomain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'participantinfo.participant': {
            'Meta': {'object_name': 'Participant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'participantinfo.participantname': {
            'Meta': {'unique_together': "(('name', 'participant'),)", 'object_name': 'ParticipantName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['participantinfo.Participant']"})
        },
        u'projectinfo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'projectinfo.license': {
            'Meta': {'object_name': 'License'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_osi_approved': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'projectinfo.project': {
            'Meta': {'object_name': 'Project'},
            'business_unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'to': u"orm['projectinfo.BusinessUnit']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'governance': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'has_contributor_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_wip': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'projects'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['projectinfo.License']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['projectinfo.Project']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'vcsinfo.branch': {
            'Meta': {'object_name': 'Branch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latest_commit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'branches'", 'to': u"orm['vcsinfo.Commit']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'vcsinfo.commit': {
            'Meta': {'unique_together': "(('repository', 'commit_id'),)", 'object_name': 'Commit'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': u"orm['vcsinfo.Committer']"}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'_parents'", 'to': u"orm['vcsinfo.Commit']", 'through': u"orm['vcsinfo.CommitEdge']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'commit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': u"orm['vcsinfo.Repository']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'vcsinfo.commitedge': {
            'Meta': {'object_name': 'CommitEdge'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Commit_parent'", 'to': u"orm['vcsinfo.Commit']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Commit_child'", 'to': u"orm['vcsinfo.Commit']"})
        },
        u'vcsinfo.committer': {
            'Meta': {'unique_together': "(('userid', 'repository'),)", 'object_name': 'Committer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'committer_ids'", 'to': u"orm['participantinfo.Participant']"}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'committers'", 'to': u"orm['vcsinfo.Repository']"}),
            'userid': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'vcsinfo.repository': {
            'Meta': {'object_name': 'Repository'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'project': ('mptt.fields.TreeForeignKey', [], {'related_name': "'repositories'", 'to': u"orm['projectinfo.Project']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'repositories'", 'to': u"orm['vcsinfo.Type']"}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10000'})
        },
        u'vcsinfo.type': {
            'Meta': {'object_name': 'Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['vcsinfo', 'mlinfo', 'btinfo', 'ircinfo', 'bloginfo', 'participantinfo']
    symmetrical = True
