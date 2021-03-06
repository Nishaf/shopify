# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-22 10:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopsify_admin', '0005_auto_20180222_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifyproductmodel',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 22, 10, 13, 35, 161420), verbose_name='Time Extracted'),
        ),
        migrations.AlterField(
            model_name='shopifysitemodel',
            name='last_update_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 22, 10, 13, 35, 159624), verbose_name='Date Updated'),
        ),
    ]
