# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-26 22:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0003_anchorset_sabr_model_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='anchorset',
            name='pitch_path',
            field=models.CharField(default='default', max_length=128),
            preserve_default=False,
        ),
    ]
