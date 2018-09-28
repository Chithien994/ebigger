# Generated by Django 2.1 on 2018-09-28 04:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import topics.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Privileged',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.IntegerField(blank=True, unique=True, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'privilegeds',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('last_action', models.DateTimeField(auto_now_add=True, verbose_name='Last Action')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(blank=True, max_length=80, null=True)),
                ('picture', models.ImageField(blank=True, default='topics/default/default.jpg', max_length=255, null=True, upload_to=topics.models.photo_upload_to)),
                ('privileged', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='privileged_topic', to='topics.Privileged')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Topics',
                'db_table': 'topics',
            },
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('last_action', models.DateTimeField(auto_now_add=True, verbose_name='Last Action')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('note_source', models.TextField(blank=True, default='', null=True)),
                ('langguage_source', models.CharField(blank=True, default='en', max_length=4)),
                ('note_meaning', models.TextField(blank=True, default='', null=True)),
                ('langguage_meaning', models.CharField(blank=True, default='en', max_length=4)),
                ('learned', models.BooleanField(default=False)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocabularys', to='topics.Topic')),
            ],
            options={
                'verbose_name_plural': 'Vocabularys',
                'db_table': 'vocabularys',
            },
        ),
    ]
