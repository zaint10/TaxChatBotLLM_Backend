# Generated by Django 4.2.11 on 2024-04-27 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_user_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='w2form',
            name='file_name',
            field=models.CharField(null=True),
        ),
    ]
