# Generated by Django 5.0.4 on 2024-05-13 10:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0019_remove_department_close_remove_department_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='date',
            field=models.TimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
