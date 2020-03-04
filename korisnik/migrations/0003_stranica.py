# Generated by Django 3.0.3 on 2020-03-04 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('korisnik', '0002_auto_20200304_2159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stranica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(default='', max_length=200)),
                ('korisnik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='korisnik.Korisnik')),
            ],
        ),
    ]
