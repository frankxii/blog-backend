# Generated by Django 3.2 on 2021-04-10 10:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='name',
        ),
        migrations.AddField(
            model_name='article',
            name='title',
            field=models.TextField(default='body'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='body',
            field=models.TextField(default=''),
            preserve_default=False,
        ),

    ]