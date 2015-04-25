# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20141121_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedhost',
            name='interface_id_ipv4',
            field=models.CharField(default=b'', max_length=16, blank=True, help_text='The IPv4 interface ID of this host. Use IPv4 notation. Empty = do not set record.', null=True, verbose_name='interface ID IPv4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relatedhost',
            name='interface_id_ipv6',
            field=models.CharField(default=b'', max_length=22, blank=True, help_text='The IPv6 interface ID of this host. Use IPv6 notation. Empty = do not set record.', null=True, verbose_name='interface ID IPv6'),
            preserve_default=True,
        ),
    ]
