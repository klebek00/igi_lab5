# Generated by Django 5.0.4 on 2024-05-12 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0011_alter_sale_сost'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='cost_prom',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
