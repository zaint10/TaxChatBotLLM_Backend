# Generated by Django 4.2.11 on 2024-04-27 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_w2form_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='w2form',
            name='messages',
            field=models.JSONField(blank=True, default='[]'),
        ),
    ]
