# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20141115_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='api_auth_faults',
            field=models.PositiveIntegerField(default=0, verbose_name='api auth faults'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='host',
            name='api_auth_result_msg',
            field=models.CharField(default=b'', max_length=255, blank=True, help_text='Latest result message relating to api authentication', null=True, verbose_name='api auth result msg'),
            preserve_default=True,
        ),
    ]
