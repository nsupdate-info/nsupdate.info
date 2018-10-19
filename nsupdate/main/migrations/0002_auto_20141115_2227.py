# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nsupdate.main.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blacklistedhost',
            options={'verbose_name': 'blacklisted host', 'verbose_name_plural': 'blacklisted hosts'},
        ),
        migrations.AlterModelOptions(
            name='domain',
            options={'verbose_name': 'domain', 'verbose_name_plural': 'domains'},
        ),
        migrations.AlterModelOptions(
            name='host',
            options={'verbose_name': 'host', 'verbose_name_plural': 'hosts'},
        ),
        migrations.AlterModelOptions(
            name='relatedhost',
            options={'verbose_name': 'related host', 'verbose_name_plural': 'related hosts'},
        ),
        migrations.AlterModelOptions(
            name='serviceupdater',
            options={'verbose_name': 'service updater', 'verbose_name_plural': 'service updaters'},
        ),
        migrations.AlterModelOptions(
            name='serviceupdaterhostconfig',
            options={'verbose_name': 'service updater host config', 'verbose_name_plural': 'service updater host configs'},
        ),
        migrations.AlterField(
            model_name='blacklistedhost',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blacklistedhost',
            name='created_by',
            field=models.ForeignKey(related_name='blacklisted_domains', verbose_name='created by', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blacklistedhost',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blacklistedhost',
            name='name_re',
            field=models.CharField(help_text='Blacklisted domain. Evaluated as regex (search).', unique=True, max_length=255, verbose_name='name RegEx'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='available',
            field=models.BooleanField(default=True, help_text="Check if nameserver is available/reachable - if not checked, we'll pause querying/updating this nameserver for a while", verbose_name='available'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='comment',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Some arbitrary comment about your domain. If your domain is public, the comment will be also publicly shown.', null=True, verbose_name='comment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='created_by',
            field=models.ForeignKey(related_name='domains', verbose_name='created by', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(help_text='Name of the zone where dynamic hosts may get added', unique=True, max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='nameserver_ip',
            field=models.GenericIPAddressField(help_text='IP where the dynamic DNS updates for this zone will be sent to', verbose_name='nameserver IP'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='nameserver_update_algorithm',
            field=models.CharField(default=b'HMAC_SHA512', help_text='HMAC_SHA512 is fine for bind9 (you can change this later, if needed)', max_length=16, verbose_name='nameserver update algorithm', choices=[(b'HMAC_SHA384', b'HMAC_SHA384'), (b'HMAC_SHA256', b'HMAC_SHA256'), (b'HMAC_SHA224', b'HMAC_SHA224'), (b'HMAC_SHA1', b'HMAC_SHA1'), (b'HMAC_MD5', b'HMAC_MD5'), (b'HMAC_SHA512', b'HMAC_SHA512')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='nameserver_update_secret',
            field=models.CharField(default=b'', help_text='Shared secret that allows updating this zone (base64 encoded)', max_length=88, verbose_name='nameserver update secret'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='public',
            field=models.BooleanField(default=False, help_text="Check to allow any user to add dynamic hosts to this zone - if not checked, we'll only allow the owner to add hosts", verbose_name='public'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='abuse',
            field=models.BooleanField(default=False, help_text='Checked if we think you abuse the service - you may uncheck this AFTER fixing all issues on your side', verbose_name='abuse'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='abuse_blocked',
            field=models.BooleanField(default=False, help_text='Checked to block a host for abuse.', verbose_name='abuse blocked'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='available',
            field=models.BooleanField(default=True, help_text="Check if host is available/in use - if not checked, we won't accept updates for this host", verbose_name='available'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='client_faults',
            field=models.PositiveIntegerField(default=0, verbose_name='client faults'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='client_result_msg',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Latest result message relating to the client', null=True, verbose_name='client result msg'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='comment',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Some arbitrary comment about your host, e.g  who / what / where this host is', null=True, verbose_name='comment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='created_by',
            field=models.ForeignKey(related_name='hosts', verbose_name='created by', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='domain',
            field=models.ForeignKey(verbose_name='domain', to='main.Domain', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='last_update_ipv4',
            field=models.DateTimeField(null=True, verbose_name='last update IPv4', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='last_update_ipv6',
            field=models.DateTimeField(null=True, verbose_name='last update IPv6', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='name',
            field=models.CharField(help_text='The name of your host.', max_length=255, verbose_name='name', validators=[django.core.validators.RegexValidator(regex=b'^(([a-z0-9][a-z0-9\\-]*[a-z0-9])|[a-z0-9])$', message=b'Invalid host name: only "a-z", "0-9" and "-" is allowed'), nsupdate.main.models.host_blacklist_validator]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='netmask_ipv4',
            field=models.PositiveSmallIntegerField(default=32, help_text='Netmask/Prefix length for IPv4.', verbose_name='netmask IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='netmask_ipv6',
            field=models.PositiveSmallIntegerField(default=64, help_text='Netmask/Prefix length for IPv6.', verbose_name='netmask IPv6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='server_faults',
            field=models.PositiveIntegerField(default=0, verbose_name='server faults'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='server_result_msg',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Latest result message relating to the server', null=True, verbose_name='server result msg'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='tls_update_ipv4',
            field=models.BooleanField(default=False, verbose_name='TLS update IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='tls_update_ipv6',
            field=models.BooleanField(default=False, verbose_name='TLS update IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='update_secret',
            field=models.CharField(max_length=64, verbose_name='update secret'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='available',
            field=models.BooleanField(default=True, help_text="Check if host is available/in use - if not checked, we won't accept updates for this host", verbose_name='available'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='comment',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Some arbitrary comment about your host, e.g  who / what / where this host is', null=True, verbose_name='comment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='interface_id_ipv4',
            field=models.CharField(default=b'', help_text='The IPv4 interface ID of this host. Use IPv4 notation.', max_length=16, verbose_name='interface ID IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='interface_id_ipv6',
            field=models.CharField(default=b'', help_text='The IPv6 interface ID of this host. Use IPv6 notation.', max_length=22, verbose_name='interface ID IPv6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='main_host',
            field=models.ForeignKey(related_name='relatedhosts', verbose_name='main host', to='main.Host', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='name',
            field=models.CharField(help_text='The name of a host in same network as your main host.', max_length=255, verbose_name='name', validators=[django.core.validators.RegexValidator(regex=b'^(([a-z0-9][a-z0-9\\-]*[a-z0-9])|[a-z0-9])$', message=b'Invalid host name: only "a-z", "0-9" and "-" is allowed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='accept_ipv4',
            field=models.BooleanField(default=False, verbose_name='accept IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='accept_ipv6',
            field=models.BooleanField(default=False, verbose_name='accept IPv6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='comment',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Some arbitrary comment about the service', null=True, verbose_name='comment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='created_by',
            field=models.ForeignKey(related_name='serviceupdater', verbose_name='created by', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='name',
            field=models.CharField(help_text='Service name', max_length=32, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='path',
            field=models.CharField(default=b'/nic/update', help_text='Update Server URL path of this service', max_length=255, verbose_name='path'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='secure',
            field=models.BooleanField(default=True, help_text='Use https / TLS to contact the Update Server?', verbose_name='secure'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdater',
            name='server',
            field=models.CharField(help_text='Update Server [name or IP] of this service', max_length=255, verbose_name='server'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='comment',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Some arbitrary comment about your host on that service', null=True, verbose_name='comment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='created_by',
            field=models.ForeignKey(related_name='serviceupdaterhostconfigs', verbose_name='created by', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='give_ipv4',
            field=models.BooleanField(default=False, verbose_name='give IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='give_ipv6',
            field=models.BooleanField(default=False, verbose_name='give IPv6'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='host',
            field=models.ForeignKey(related_name='serviceupdaterhostconfigs', verbose_name='host', to='main.Host', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='hostname',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='The hostname for that service (used in query string)', null=True, verbose_name='hostname'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='name',
            field=models.CharField(help_text='The name/id for that service (used for http basic auth)', max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='password',
            field=models.CharField(help_text='The password/secret for that service (used for http basic auth)', max_length=255, verbose_name='password'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceupdaterhostconfig',
            name='service',
            field=models.ForeignKey(verbose_name='service', to='main.ServiceUpdater', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
