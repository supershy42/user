# Generated by Django 5.1.4 on 2024-12-27 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0004_merge_0003_alter_user_avatar_0003_user_is_2fa_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='avatars/default.png', upload_to='avatars/'),
        ),
    ]
