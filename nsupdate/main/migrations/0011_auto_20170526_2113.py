# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20151229_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(help_text='Name of the zone where dynamic hosts may get added', unique=True, max_length=255, verbose_name='name', validators=[django.core.validators.RegexValidator(regex=b'([a-zA-Z0-9-_]+\\.)+[a-zA-Z0-9-_]{2,}', message='Invalid domain name')]),
        ),
    ]
