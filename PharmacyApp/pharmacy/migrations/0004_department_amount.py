# Generated by Django 5.0.4 on 2024-05-11 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_vacancy_need'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='amount',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
