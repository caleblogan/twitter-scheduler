# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-05 19:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('twitterscheduler', '0004_auto_20170904_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_sync_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 5, 18, 36, 53, 925365, tzinfo=utc)),
        ),
    ]
