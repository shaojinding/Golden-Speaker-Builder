# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-29 20:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speech', '0041_auto_20181029_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anchorset',
            name='used',
        ),
    ]