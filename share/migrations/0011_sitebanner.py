# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-12 15:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0010_auto_20161212_1418_e'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('color', models.IntegerField(choices=[(0, 'success'), (1, 'info'), (2, 'warning'), (3, 'danger')], default=1)),
                ('icon', models.CharField(blank=True, default='exclamation', max_length=31)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
