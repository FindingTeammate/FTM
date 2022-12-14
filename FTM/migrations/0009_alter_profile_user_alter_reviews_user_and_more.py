# Generated by Django 4.1.2 on 2022-10-19 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FTM', '0008_alter_profile_user_alter_reviews_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FTM.profile'),
        ),
        migrations.AlterField(
            model_name='workexp',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FTM.profile'),
        ),
    ]
