# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20141121_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='staleness',
            field=models.PositiveIntegerField(default=0, verbose_name='staleness'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='host',
            name='staleness_notification_timestamp',
            field=models.DateTimeField(null=True, verbose_name='staleness notification time', blank=True),
            preserve_default=True,
        ),
    ]
