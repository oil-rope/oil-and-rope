# Generated by Django 3.2.5 on 2021-08-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_menu', '0003_auto_20210727_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicmenu',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]