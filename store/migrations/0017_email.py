# Generated by Django 5.0.7 on 2024-08-25 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
