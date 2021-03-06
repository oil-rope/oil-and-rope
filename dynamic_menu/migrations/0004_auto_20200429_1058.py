# Generated by Django 2.2.12 on 2020-04-29 08:58

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_menu', '0003_auto_20191211_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicmenu',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='dynamic_menu.DynamicMenu', verbose_name='Parent Menu'),
        ),
    ]
