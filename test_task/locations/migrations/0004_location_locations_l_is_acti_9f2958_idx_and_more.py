# Generated by Django 5.2.3 on 2025-06-25 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0003_alter_category_options"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="location",
            index=models.Index(
                fields=["is_active"], name="locations_l_is_acti_9f2958_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(
                fields=["view_count"], name="locations_l_view_co_c3995a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(
                fields=["created_at"], name="locations_l_created_c17f75_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(fields=["name"], name="locations_l_name_0dcc82_idx"),
        ),
        migrations.AddIndex(
            model_name="location",
            index=models.Index(
                fields=["description"], name="locations_l_descrip_29d5bc_idx"
            ),
        ),
    ]
