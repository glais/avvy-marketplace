# Generated by Django 3.2.19 on 2023-06-09 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_domain_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='hash',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
