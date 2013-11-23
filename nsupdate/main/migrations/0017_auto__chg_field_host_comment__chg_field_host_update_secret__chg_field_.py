# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Host.comment'
        db.alter_column(u'main_host', 'comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Host.update_secret'
        db.alter_column(u'main_host', 'update_secret', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'Host.subdomain'
        db.alter_column(u'main_host', 'subdomain', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'BlacklistedDomain.domain'
        db.alter_column(u'main_blacklisteddomain', 'domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))

        # Changing field 'Domain.nameserver_update_algorithm'
        db.alter_column(u'main_domain', 'nameserver_update_algorithm', self.gf('django.db.models.fields.CharField')(max_length=16))

        # Changing field 'Domain.domain'
        db.alter_column(u'main_domain', 'domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))

        # Changing field 'Domain.nameserver_update_key'
        db.alter_column(u'main_domain', 'nameserver_update_key', self.gf('django.db.models.fields.CharField')(max_length=88))

        # Changing field 'Domain.comment'
        db.alter_column(u'main_domain', 'comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Host.comment'
        db.alter_column(u'main_host', 'comment', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'Host.update_secret'
        db.alter_column(u'main_host', 'update_secret', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Host.subdomain'
        db.alter_column(u'main_host', 'subdomain', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'BlacklistedDomain.domain'
        db.alter_column(u'main_blacklisteddomain', 'domain', self.gf('django.db.models.fields.CharField')(max_length=256, unique=True))

        # Changing field 'Domain.nameserver_update_algorithm'
        db.alter_column(u'main_domain', 'nameserver_update_algorithm', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Domain.domain'
        db.alter_column(u'main_domain', 'domain', self.gf('django.db.models.fields.CharField')(max_length=256, unique=True))

        # Changing field 'Domain.nameserver_update_key'
        db.alter_column(u'main_domain', 'nameserver_update_key', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Domain.comment'
        db.alter_column(u'main_domain', 'comment', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'main.domain': {
            'Meta': {'object_name': 'Domain'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'nameserver_ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'nameserver_update_algorithm': ('django.db.models.fields.CharField', [], {'default': "'HMAC_SHA512'", 'max_length': '16'}),
            'nameserver_update_key': ('django.db.models.fields.CharField', [], {'max_length': '88'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'main.host': {
            'Meta': {'unique_together': "(('subdomain', 'domain'),)", 'object_name': 'Host'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hosts'", 'to': u"orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_update_ipv4': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_update_ipv6': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ssl_update_ipv4': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ssl_update_ipv6': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_secret': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['main']