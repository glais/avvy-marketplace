# Generated by Django 3.2.19 on 2023-06-09 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
