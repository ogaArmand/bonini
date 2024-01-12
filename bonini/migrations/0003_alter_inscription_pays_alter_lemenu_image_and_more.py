# Generated by Django 4.1.8 on 2024-01-09 14:41

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bonini', '0002_lemenu_estactif'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='pays',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='lemenu',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='typemenu',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]