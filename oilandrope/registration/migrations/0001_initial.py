# Generated by Django 2.2.2 on 2019-07-30 14:54

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('bio', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Biography')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Birthday')),
                ('language', models.CharField(choices=[('af', 'Afrikaans'), ('sq', 'Albanian'), ('ar', 'Arabic'), ('es-ar', 'Argentinian Spanish'), ('hy', 'Armenian'), ('ast', 'Asturian'), ('en-au', 'Australian English'), ('az', 'Azerbaijani'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bs', 'Bosnian'), ('pt-br', 'Brazilian Portuguese'), ('br', 'Breton'), ('en-gb', 'British English'), ('bg', 'Bulgarian'), ('my', 'Burmese'), ('ca', 'Catalan'), ('es-co', 'Colombian Spanish'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('gl', 'Galician'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('io', 'Ido'), ('id', 'Indonesian'), ('ia', 'Interlingua'), ('ga', 'Irish'), ('it', 'Italian'), ('ja', 'Japanese'), ('kab', 'Kabyle'), ('kn', 'Kannada'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('ko', 'Korean'), ('lv', 'Latvian'), ('lt', 'Lithuanian'), ('dsb', 'Lower Sorbian'), ('lb', 'Luxembourgish'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mr', 'Marathi'), ('es-mx', 'Mexican Spanish'), ('mn', 'Mongolian'), ('ne', 'Nepali'), ('es-ni', 'Nicaraguan Spanish'), ('nb', 'Norwegian Bokmål'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('fa', 'Persian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pa', 'Punjabi'), ('ro', 'Romanian'), ('ru', 'Russian'), ('gd', 'Scottish Gaelic'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('zh-hans', 'Simplified Chinese'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('es', 'Spanish'), ('sw', 'Swahili'), ('sv', 'Swedish'), ('ta', 'Tamil'), ('tt', 'Tatar'), ('te', 'Telugu'), ('th', 'Thai'), ('zh-hant', 'Traditional Chinese'), ('tr', 'Turkish'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('hsb', 'Upper Sorbian'), ('ur', 'Urdu'), ('es-ve', 'Venezuelan Spanish'), ('vi', 'Vietnamese'), ('cy', 'Welsh')], default='en-us', max_length=30, verbose_name='Language')),
                ('alias', models.CharField(blank=True, max_length=30, null=True, verbose_name='Alias')),
                ('web', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('image', models.ImageField(blank=True, null=True, upload_to='registration/profile', verbose_name='Avatar')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Profiles',
                'ordering': ['user__first_name'],
                'verbose_name': 'Profile',
            },
        ),
    ]
