# Generated by Django 4.1.4 on 2022-12-31 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_juego_appid'),
    ]

    operations = [
        migrations.AddField(
            model_name='juego',
            name='desarrollador',
            field=models.TextField(null=True, verbose_name='Desarrollador'),
        ),
        migrations.AddField(
            model_name='juego',
            name='editor',
            field=models.TextField(null=True, verbose_name='Editor'),
        ),
    ]
