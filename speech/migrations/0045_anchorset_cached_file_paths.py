# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-30 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0044_remove_anchorset_pitch_model_dir'),
    ]

    operations = [
        migrations.AddField(
            model_name='anchorset',
            name='cached_file_paths',
            field=models.CharField(default='[""]', max_length=4000),
        ),
    ]
