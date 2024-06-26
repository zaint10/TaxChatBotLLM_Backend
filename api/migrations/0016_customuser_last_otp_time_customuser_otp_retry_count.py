# Generated by Django 4.2.11 on 2024-04-30 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_customuser_is_2fa_enabled_customuser_lockout_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_otp_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_retry_count',
            field=models.IntegerField(default=0),
        ),
    ]
