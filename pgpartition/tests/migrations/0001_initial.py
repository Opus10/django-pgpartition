# Generated by Django 3.2.16 on 2022-10-27 11:36

from django.db import migrations, models
import django.db.models.deletion
import pgpartition


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partition',
            fields=[
                ('created_at', models.DateTimeField(primary_key=True, serialize=False)),
                ('int_field', models.IntegerField()),
            ],
            options={
                'partition': pgpartition.Partition(control=['created_at'], interval='daily', key=['created_at'], method='RANGE', premake=None, start_partition=None),
            },
        ),
        migrations.CreateModel(
            name='PartitionFK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.partition')),
            ],
        ),
    ]
