# Generated by Django 5.0.4 on 2024-05-12 15:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0008_remove_department_medicines_department_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='medicine',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='pharmacy.medicines'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='SaleItem',
        ),
    ]
