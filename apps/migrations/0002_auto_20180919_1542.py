# Generated by Django 2.1 on 2018-09-19 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appinfo',
            options={'verbose_name_plural': 'AppInfos'},
        ),
        migrations.AlterModelTable(
            name='appinfo',
            table='appinfos',
        ),
    ]
