# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-18 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0036_anchorset_cached_file_dir'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anchorset',
            name='cached_file_dir',
        ),
    ]