# Generated by Django 4.0 on 2022-02-04 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='entry_created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='entry created at'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='entry_updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='entry updated at'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='identifier'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='entry_created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='entry created at'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='entry_updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='entry updated at'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='identifier'),
        ),
    ]
