# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-31 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0004_update_trigger_migrations_20161025_1455'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rawdata',
            unique_together=set([('provider_doc_id', 'app_label', 'source', 'sha256')]),
        ),
    ]