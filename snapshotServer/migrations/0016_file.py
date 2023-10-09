# Generated by Django 3.2.18 on 2023-08-31 13:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0015_stepreference_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='documents/%Y/%m/%d')),
                ('stepResult', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='snapshotServer.stepresult')),
            ],
        ),
    ]
