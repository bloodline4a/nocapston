# Generated by Django 4.2.7 on 2023-11-23 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0003_alter_admin_uname'),
    ]

    operations = [
        migrations.AddField(
            model_name='booked',
            name='image',
            field=models.ImageField(default='image', upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='uname',
            field=models.CharField(max_length=255),
        ),
    ]
