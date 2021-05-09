# Generated by Django 3.2 on 2021-05-02 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_category_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='标签名称')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.JSONField(default=list),
        ),
    ]