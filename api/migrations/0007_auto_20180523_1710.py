# Generated by Django 2.0.3 on 2018-05-23 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20180514_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='judge_spec',
        ),
        migrations.AddField(
            model_name='judgespec',
            name='problem',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='judge_spec', to='api.Problem'),
            preserve_default=False,
        ),
    ]
