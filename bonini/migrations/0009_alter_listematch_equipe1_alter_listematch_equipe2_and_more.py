# Generated by Django 4.1.8 on 2024-01-11 20:05

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bonini', '0008_remove_commande_detail_etat_commande_estfacture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listematch',
            name='equipe1',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='listematch',
            name='equipe2',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='niveaumatch',
            name='date_debut',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='niveaumatch',
            name='date_fin',
            field=models.DateField(null=True),
        ),
    ]
