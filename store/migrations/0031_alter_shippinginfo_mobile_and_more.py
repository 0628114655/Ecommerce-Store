# Generated by Django 5.0.7 on 2024-09-03 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0030_shippinginfo_remove_orderitem_item_cart_ordered_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippinginfo',
            name='mobile',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shippinginfo',
            name='zip_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
