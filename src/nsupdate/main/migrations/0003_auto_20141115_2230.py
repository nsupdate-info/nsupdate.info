# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20141115_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='nameserver2_ip',
            field=models.GenericIPAddressField(help_text='IP of additional nameserver (used for queries)', null=True, verbose_name='nameserver IP (secondary)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='domain',
            name='nameserver_ip',
            field=models.GenericIPAddressField(help_text='IP where the dynamic DNS updates for this zone will be sent to', verbose_name='nameserver IP (primary)'),
            preserve_default=True,
        ),
    ]
