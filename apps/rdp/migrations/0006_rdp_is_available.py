# Generated by Django 5.0.3 on 2025-05-04 19:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rdp", "0005_rdp_hosting_rdp_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="rdp",
            name="is_available",
            field=models.BooleanField(default=True),
        ),
    ]
