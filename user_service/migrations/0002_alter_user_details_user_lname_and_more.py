# Generated by Django 5.0.3 on 2024-03-19 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='user_lname',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='user_mname',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
