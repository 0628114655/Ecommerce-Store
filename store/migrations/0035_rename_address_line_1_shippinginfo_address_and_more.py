# Generated by Django 5.0.7 on 2024-09-05 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_alter_cart_shipping_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippinginfo',
            old_name='address_line_1',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='shippinginfo',
            old_name='first_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='shippinginfo',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='shippinginfo',
            name='last_name',
        ),
    ]
