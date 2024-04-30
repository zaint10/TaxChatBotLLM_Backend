# Generated by Django 4.2.11 on 2024-04-30 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_customuser_secret_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_2fa_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='lockout_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
