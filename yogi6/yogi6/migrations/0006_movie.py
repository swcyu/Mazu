# Generated by Django 3.2.15 on 2022-09-28 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yogi6', '0005_summary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('movie_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('poster_link', models.CharField(blank=True, max_length=500, null=True)),
                ('director', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'movie',
                'managed': False,
            },
        ),
    ]
