# Generated by Django 5.0.6 on 2024-07-09 09:50

import datetime
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('justyummy', '0002_product_flashsaleprice_product_productprice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='publishDate',
            field=models.DateField(auto_created=datetime.datetime(2024, 7, 9, 10, 50, 19, 615707)),
        ),
        migrations.AlterField(
            model_name='customerpurchasedorders',
            name='purchaseDate',
            field=models.DateField(auto_created='2024-07-09T10:50:19.614708'),
        ),
        migrations.AlterField(
            model_name='customerreciept',
            name='create_at',
            field=models.DateTimeField(auto_created='2024-07-09T10:50:19.612707'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 9, 10, 50, 19, 611706)),
        ),
        migrations.AlterField(
            model_name='product',
            name='productCategory',
            field=models.CharField(choices=[('phone', 'Phone'), ('computer', 'Computer'), ('wristwatch', 'Wristwatch'), ('camera', 'Camera'), ('headphone', 'Headphone'), ('gaming', 'Gaming'), ('shoe, shoe', 'Shoe'), ('jewelry', 'Jewelry'), ('clothe', 'Clothe'), ('perfume', 'Perfume'), ('necklace', 'Necklace'), ('electronic', 'Electronic'), ('toy', 'Toy'), ('none', 'None')], default='none', max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='productDesignation',
            field=models.CharField(choices=[('men', 'Men'), ('women', 'Women'), ('both', 'Both'), ('children', 'Children'), ('baby', 'Baby'), ('all', 'All')], default='all', max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='productId',
            field=models.UUIDField(auto_created=uuid.UUID('b8d9ba08-cfac-4a1e-bb55-2d0a1ed4ce6c'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='update_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 9, 10, 50, 19, 611706)),
        ),
    ]
