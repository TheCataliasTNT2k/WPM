# Generated by Django 4.0.4 on 2022-06-26 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='peer',
            name='valid',
            field=models.BooleanField(default=False),
        ),
    ]
