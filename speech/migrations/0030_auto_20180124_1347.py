# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-24 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0029_goldenspeaker_select_phoneme_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anchorset',
            name='aborted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anchorset',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anchorset',
            name='built',
            field=models.CharField(default='False', max_length=128),
        ),
        migrations.AlterField(
            model_name='anchorset',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anchorset',
            name='modified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anchorset',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
