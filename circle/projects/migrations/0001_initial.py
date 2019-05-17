# Generated by Django 2.2.1 on 2019-05-17 19:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Project <built-in function id>', max_length=150, unique=True)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('requirements', models.CharField(blank=True, max_length=500)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('filled', models.BooleanField(default=False)),
                ('time', models.CharField(blank=True, max_length=100)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='projects.Project')),
                ('skills', models.ManyToManyField(blank=True, related_name='positions', to='accounts.Skill')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='positions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applied', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.BooleanField(default=True)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicants', to='projects.Position')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-applied',),
            },
        ),
    ]
