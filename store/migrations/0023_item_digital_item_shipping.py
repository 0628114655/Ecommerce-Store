# Generated by Django 5.0.7 on 2024-08-29 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_rename_favorites_favorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='digital',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='shipping',
            field=models.FloatField(default=0),
        ),
    ]
