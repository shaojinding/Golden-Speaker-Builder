# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-24 21:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0024_anchorset_aborted'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenspeaker',
            name='aborted',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
