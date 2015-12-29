# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='domain',
            options={'ordering': ('name',), 'verbose_name': 'domain', 'verbose_name_plural': 'domains'},
        ),
        migrations.AlterModelOptions(
            name='host',
            options={'ordering': ('domain', 'name'), 'verbose_name': 'host', 'verbose_name_plural': 'hosts'},
        ),
        migrations.AlterModelOptions(
            name='relatedhost',
            options={'ordering': ('main_host', 'name'), 'verbose_name': 'related host', 'verbose_name_plural': 'related hosts'},
        ),
    ]
