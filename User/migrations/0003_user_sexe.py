# Generated by Django 4.1.13 on 2024-02-13 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0002_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sexe',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
