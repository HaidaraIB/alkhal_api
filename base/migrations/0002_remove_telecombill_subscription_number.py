# Generated by Django 5.0.4 on 2024-05-05 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telecombill',
            name='subscription_number',
        ),
    ]