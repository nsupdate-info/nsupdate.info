# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Removing index on 'Host', fields ['subdomain', 'domain']
        db.delete_index(u'main_host', ['subdomain', 'domain_id'])

        # Renaming field 'Host.subdomain'
        db.rename_column(u'main_host', 'subdomain', 'name')

        # Renaming field 'Domain.domain'
        db.rename_column(u'main_domain', 'domain', 'name')

        # Renaming field 'BlacklistedDomain.domain'
        db.rename_column(u'main_blacklisteddomain', 'domain', 'name_re')

        # Adding index on 'Host', fields ['name', 'domain']
        db.create_index(u'main_host', ['name', 'domain_id'])

    def backwards(self, orm):
        # Removing index on 'Host', fields ['name', 'domain']
        db.delete_index(u'main_host', ['name', 'domain_id'])

        # Renaming field 'Host.subdomain'
        db.rename_column(u'main_host', 'name', 'subdomain')

        # Renaming field 'Domain.domain'
        db.rename_column(u'main_domain', 'name', 'domain')

        # Renaming field 'BlacklistedDomain.domain'
        db.rename_column(u'main_blacklisteddomain', 'name_re', 'domain')

        # Adding index on 'Host', fields ['subdomain', 'domain']
        db.create_index(u'main_host', ['subdomain', 'domain_id'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.blacklisteddomain': {
            'Meta': {'object_name': 'BlacklistedDomain'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blacklisted_domains'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name_re': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'main.domain': {
            'Meta': {'object_name': 'Domain'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'domains'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'nameserver_ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'nameserver_update_algorithm': ('django.db.models.fields.CharField', [], {'default': "'HMAC_SHA512'", 'max_length': '16'}),
            'nameserver_update_secret': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '88'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'main.host': {
            'Meta': {'unique_together': "(('name', 'domain'),)", 'object_name': 'Host', 'index_together': "(('name', 'domain'),)"},
            'abuse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'client_faults': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'client_result_msg': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hosts'", 'to': u"orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_update_ipv4': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_update_ipv6': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_faults': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'server_result_msg': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tls_update_ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tls_update_ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_secret': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'main.serviceupdater': {
            'Meta': {'object_name': 'ServiceUpdater'},
            'accept_ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accept_ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serviceupdater'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'path': ('django.db.models.fields.CharField', [], {'default': "'/nic/update'", 'max_length': '255'}),
            'secure': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'main.serviceupdaterhostconfig': {
            'Meta': {'object_name': 'ServiceUpdaterHostConfig'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serviceupdaterhostconfigs'", 'to': u"orm['auth.User']"}),
            'give_ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'give_ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serviceupdaterhostconfigs'", 'to': u"orm['main.Host']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.ServiceUpdater']"})
        }
    }

    complete_apps = ['main']
