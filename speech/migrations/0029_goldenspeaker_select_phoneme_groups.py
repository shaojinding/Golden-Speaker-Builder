# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-10 19:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0028_goldenspeaker_tempo_scale'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenspeaker',
            name='select_phoneme_groups',
            field=models.CharField(default='[]', max_length=1000),
            preserve_default=False,
        ),
    ]