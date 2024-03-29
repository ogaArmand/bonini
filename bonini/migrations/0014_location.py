# Generated by Django 4.1.8 on 2024-01-12 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bonini', '0013_commande_nbarticle'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.CharField(max_length=255)),
                ('longitude', models.CharField(max_length=255)),
                ('inscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bonini.inscription')),
            ],
        ),
    ]
