# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-31 17:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0045_anchorset_cached_file_paths'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anchorset',
            name='pitch_model_built',
        ),
        migrations.RemoveField(
            model_name='sourcemodel',
            name='cached_file_dir',
        ),
        migrations.AddField(
            model_name='anchorset',
            name='pitch_model_dir',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='sourcemodel',
            name='cached_file_paths',
            field=models.CharField(default='[""]', max_length=4000),
        ),
    ]
