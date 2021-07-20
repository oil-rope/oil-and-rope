# Generated by Django 3.2.4 on 2021-06-30 16:11

from django.db import migrations, models
import django.db.models.deletion
import dynamic_menu.models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dynamic_menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicmenu',
            name='appended_text',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='appended text'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='description_es',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='extra_urls_args',
            field=models.CharField(blank=True, max_length=254, null=True, verbose_name='extra parameters'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='icon',
            field=models.FileField(blank=True, max_length=254, null=True, upload_to=dynamic_menu.models.dynamic_menu_path, verbose_name='icon'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='menu_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Standard menu'), (1, 'Context menu')], default=0, verbose_name='menu type'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='name_es',
            field=models.CharField(max_length=100, null=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='dynamic_menu.dynamicmenu', verbose_name='parent menu'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='permissions_required',
            field=models.ManyToManyField(blank=True, related_name='menus', to='auth.Permission', verbose_name='permissions required'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='prepended_text',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='prepended text'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='related_models',
            field=models.ManyToManyField(blank=True, related_name='menus', to='contenttypes.ContentType', verbose_name='related models'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='staff_required',
            field=models.BooleanField(default=False, verbose_name='staff required'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='superuser_required',
            field=models.BooleanField(default=False, verbose_name='superuser required'),
        ),
        migrations.AlterField(
            model_name='dynamicmenu',
            name='url_resolver',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='resolver'),
        ),
    ]
