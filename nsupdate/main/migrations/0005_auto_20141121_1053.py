# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20141115_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='nameserver2_ip',
            field=models.GenericIPAddressField(help_text='IP where DNS queries for this zone will be sent to', null=True, verbose_name='nameserver IP (secondary)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='host',
            name='tls_update_ipv6',
            field=models.BooleanField(default=False, verbose_name='TLS update IPv6'),
            preserve_default=True,
        ),
    ]
