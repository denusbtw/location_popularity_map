# Generated by Django 5.2.3 on 2025-06-25 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="location",
            unique_together={("latitude", "longitude")},
        ),
    ]
