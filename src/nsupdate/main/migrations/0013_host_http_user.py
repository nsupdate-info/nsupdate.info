# Generated by Django 2.2.9 on 2020-01-10 08:53

from django.db import migrations, models
import nsupdate.main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20191230_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='http_user',
            field=models.CharField(default=nsupdate.main.models._http_user_generator, max_length=30, unique=True, verbose_name='http user'),
        ),
    ]