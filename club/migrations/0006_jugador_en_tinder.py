# Generated by Django 5.2.3 on 2025-06-18 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0005_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='jugador',
            name='en_tinder',
            field=models.BooleanField(default=True, help_text='¿Acepta aparecer en el emparejador tipo Tinder?'),
        ),
    ]
