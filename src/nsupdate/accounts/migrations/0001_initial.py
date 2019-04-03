# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='user', on_delete=models.CASCADE)),
                ('language', models.CharField(default=b'', choices=[(b'en', b'English'), (b'de', b'German'), (b'fr', b'French'), (b'it', b'Italian'), (b'pl', b'Polish'), (b'zh-cn', b'Chinese (China)')], max_length=10, blank=True, null=True, verbose_name='language')),
            ],
            options={
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
            },
            bases=(models.Model,),
        ),
    ]
