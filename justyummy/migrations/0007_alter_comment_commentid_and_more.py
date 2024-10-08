# Generated by Django 5.0.6 on 2024-08-21 11:48

import datetime
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('justyummy', '0006_alter_comment_commentid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='commentId',
            field=models.UUIDField(default=uuid.UUID('3bfcb86b-3b95-402a-8abb-28c24e75bdcf'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customerbilligdetails',
            name='billingDetailId',
            field=models.UUIDField(auto_created=uuid.UUID('9fc03aee-ea19-4272-8288-f57cabda89c7'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customerbilligdetails',
            name='create_at',
            field=models.DateField(default=datetime.datetime(2024, 8, 21, 11, 48, 33, 414321, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='customerorders',
            name='orderId',
            field=models.UUIDField(default=uuid.UUID('55af53dc-973a-4b3b-ae59-e7eedc3fce9d'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customerreciept',
            name='receiptId',
            field=models.UUIDField(default=uuid.UUID('fb80f3fd-349f-44e1-a191-2188f00356e1'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='productId',
            field=models.UUIDField(default=uuid.UUID('3ca4c81d-0675-47c4-8343-8a2b05e94e60'), primary_key=True, serialize=False),
        ),
    ]
