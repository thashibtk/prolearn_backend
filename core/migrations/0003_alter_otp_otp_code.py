# Generated by Django 5.1.6 on 2025-02-17 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='otp_code',
            field=models.IntegerField(),
        ),
    ]
