# Generated by Django 2.1.5 on 2019-02-13 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0004_auto_20190211_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article_updown',
            name='up',
            field=models.BooleanField(null=True, verbose_name='是否赞'),
        ),
    ]
