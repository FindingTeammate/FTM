# Generated by Django 4.1.2 on 2022-10-17 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FTM', '0002_remove_reviews_profile_remove_workexp_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_user',
            field=models.CharField(default='', max_length=6, unique=True),
        ),
    ]
