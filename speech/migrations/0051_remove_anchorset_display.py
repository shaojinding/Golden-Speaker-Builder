# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-06 16:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0050_goldenspeaker_output_wav_dir'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anchorset',
            name='display',
        ),
    ]
