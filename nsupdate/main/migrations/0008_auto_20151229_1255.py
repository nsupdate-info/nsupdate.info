# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150425_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='available',
            field=models.BooleanField(default=False, help_text="Check if nameserver is available/reachable - if not checked, we'll pause querying/updating this nameserver for a while", verbose_name='available'),
        ),
    ]
