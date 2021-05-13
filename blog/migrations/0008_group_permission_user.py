# Generated by Django 3.2 on 2021-05-13 11:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20210507_2257'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True, verbose_name='组名')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=15, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=128, verbose_name='密码')),
                ('is_active', models.BooleanField(default=True, verbose_name='激活')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='上次登录时间')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('group', models.ManyToManyField(db_constraint=False, to='blog.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, verbose_name='权限名')),
                ('group', models.ManyToManyField(db_constraint=False, to='blog.Group')),
            ],
        ),
    ]
