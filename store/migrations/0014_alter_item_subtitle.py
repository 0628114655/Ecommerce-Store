# Generated by Django 5.0.7 on 2024-08-23 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_item_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='subtitle',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
