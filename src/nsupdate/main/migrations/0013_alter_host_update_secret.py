# Generated by Django 4.1.5 on 2023-03-07 16:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0012_auto_20191230_1729"),
    ]

    operations = [
        migrations.AlterField(
            model_name="host",
            name="update_secret",
            field=models.CharField(max_length=128, verbose_name="update secret"),
        ),
    ]
