# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nsupdate.main.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistedHost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_re', models.CharField(help_text='Blacklisted domain. Evaluated as regex (search).', unique=True, max_length=255)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name=u'blacklisted_domains', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the zone where dynamic hosts may get added', unique=True, max_length=255)),
                ('nameserver_ip', models.GenericIPAddressField(help_text='IP where the dynamic DNS updates for this zone will be sent to')),
                ('nameserver_update_secret', models.CharField(default=b'', help_text='Shared secret that allows updating this zone (base64 encoded)', max_length=88)),
                ('nameserver_update_algorithm', models.CharField(default=b'HMAC_SHA512', help_text='HMAC_SHA512 is fine for bind9 (you can change this later, if needed)', max_length=16, choices=[(b'HMAC_SHA384', b'HMAC_SHA384'), (b'HMAC_SHA256', b'HMAC_SHA256'), (b'HMAC_SHA224', b'HMAC_SHA224'), (b'HMAC_SHA1', b'HMAC_SHA1'), (b'HMAC_MD5', b'HMAC_MD5'), (b'HMAC_SHA512', b'HMAC_SHA512')])),
                ('public', models.BooleanField(default=False, help_text="Check to allow any user to add dynamic hosts to this zone - if not checked, we'll only allow the owner to add hosts")),
                ('available', models.BooleanField(default=True, help_text="Check if nameserver is available/reachable - if not checked, we'll pause querying/updating this nameserver for a while")),
                ('comment', models.CharField(default=b'', max_length=255, null=True, help_text='Some arbitrary comment about your domain. If your domain is public, the comment will be also publicly shown.', blank=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name=u'domains', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name of your host.', max_length=255, validators=[django.core.validators.RegexValidator(regex=b'^(([a-z0-9][a-z0-9\\-]*[a-z0-9])|[a-z0-9])$', message=b'Invalid host name: only "a-z", "0-9" and "-" is allowed'), nsupdate.main.models.host_blacklist_validator])),
                ('update_secret', models.CharField(max_length=64)),
                ('comment', models.CharField(default=b'', max_length=255, null=True, help_text='Some arbitrary comment about your host, e.g  who / what / where this host is', blank=True)),
                ('available', models.BooleanField(default=True, help_text="Check if host is available/in use - if not checked, we won't accept updates for this host")),
                ('netmask_ipv4', models.PositiveSmallIntegerField(default=32, help_text='Netmask/Prefix length for IPv4.')),
                ('netmask_ipv6', models.PositiveSmallIntegerField(default=64, help_text='Netmask/Prefix length for IPv6.')),
                ('abuse', models.BooleanField(default=False, help_text='Checked if we think you abuse the service - you may uncheck this AFTER fixing all issues on your side')),
                ('abuse_blocked', models.BooleanField(default=False, help_text='Checked to block a host for abuse.')),
                ('client_faults', models.PositiveIntegerField(default=0)),
                ('client_result_msg', models.CharField(default=b'', max_length=255, null=True, help_text='Latest result message relating to the client', blank=True)),
                ('server_faults', models.PositiveIntegerField(default=0)),
                ('server_result_msg', models.CharField(default=b'', max_length=255, null=True, help_text='Latest result message relating to the server', blank=True)),
                ('last_update_ipv4', models.DateTimeField(null=True, blank=True)),
                ('last_update_ipv6', models.DateTimeField(null=True, blank=True)),
                ('tls_update_ipv4', models.BooleanField(default=False)),
                ('tls_update_ipv6', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name=u'hosts', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('domain', models.ForeignKey(to='main.Domain', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelatedHost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The name of a host in same network as your main host.', max_length=255, validators=[django.core.validators.RegexValidator(regex=b'^(([a-z0-9][a-z0-9\\-]*[a-z0-9])|[a-z0-9])$', message=b'Invalid host name: only "a-z", "0-9" and "-" is allowed')])),
                ('comment', models.CharField(default=b'', max_length=255, null=True, help_text='Some arbitrary comment about your host, e.g  who / what / where this host is', blank=True)),
                ('interface_id_ipv4', models.CharField(default=b'', help_text='The IPv4 interface ID of this host. Use IPv4 notation.', max_length=16)),
                ('interface_id_ipv6', models.CharField(default=b'', help_text='The IPv6 interface ID of this host. Use IPv6 notation.', max_length=22)),
                ('available', models.BooleanField(default=True, help_text="Check if host is available/in use - if not checked, we won't accept updates for this host")),
                ('main_host', models.ForeignKey(related_name=u'relatedhosts', to='main.Host', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceUpdater',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Service name', max_length=32)),
                ('comment', models.CharField(default=b'', max_length=255, null=True, help_text='Some arbitrary comment about the service', blank=True)),
                ('server', models.CharField(help_text='Update Server [name or IP] of this service', max_length=255)),
                ('path', models.CharField(default=b'/nic/update', help_text='Update Server URL path of this service', max_length=255)),
                ('secure', models.BooleanField(default=True, help_text='Use https / TLS to contact the Update Server?')),
                ('accept_ipv4', models.BooleanField(default=False)),
                ('accept_ipv6', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name=u'serviceupdater', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceUpdaterHostConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(default=b'', max_length=255, null=True, help_text='The hostname for that service (used in query string)', blank=True)),
                ('comment', models.CharField(default=b'', max_length=255, null=True, help_text='Some arbitrary comment about your host on that service', blank=True)),
                ('name', models.CharField(help_text='The name/id for that service (used for http basic auth)', max_length=255)),
                ('password', models.CharField(help_text='The password/secret for that service (used for http basic auth)', max_length=255)),
                ('give_ipv4', models.BooleanField(default=False)),
                ('give_ipv6', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(related_name=u'serviceupdaterhostconfigs', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('host', models.ForeignKey(related_name=u'serviceupdaterhostconfigs', to='main.Host', on_delete=models.CASCADE)),
                ('service', models.ForeignKey(to='main.ServiceUpdater', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='relatedhost',
            unique_together=set([('name', 'main_host')]),
        ),
        migrations.AlterUniqueTogether(
            name='host',
            unique_together=set([('name', 'domain')]),
        ),
        migrations.AlterIndexTogether(
            name='host',
            index_together=set([('name', 'domain')]),
        ),
    ]
