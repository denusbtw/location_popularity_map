# Generated by Django 5.2.3 on 2025-06-25 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_alter_location_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["name"], "verbose_name_plural": "Categories"},
        ),
    ]
