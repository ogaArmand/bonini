# Generated by Django 4.1.8 on 2024-01-11 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonini', '0009_alter_listematch_equipe1_alter_listematch_equipe2_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='lematch',
            new_name='commende_match',
        ),
        migrations.AddField(
            model_name='listematch',
            name='estencours',
            field=models.BooleanField(default=False),
        ),
    ]
