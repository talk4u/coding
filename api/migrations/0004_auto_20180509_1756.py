# Generated by Django 2.0.3 on 2018-05-09 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180426_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='judgespec',
            name='mem_limit_bytes',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='judgespec',
            name='time_limit_seconds',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]