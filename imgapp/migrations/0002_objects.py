# Generated by Django 2.2.1 on 2019-06-27 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imgapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Objects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objectslist', models.CharField(max_length=4000)),
            ],
        ),
    ]
