# Generated by Django 5.0.3 on 2025-01-17 20:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shells", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shell",
            name="ssl",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="shell",
            name="tld",
            field=models.CharField(default="com", max_length=10),
        ),
    ]
