# Generated by Django 5.0 on 2024-10-22 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ask_questions_app', '0007_alter_question_question_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255)),
                ('expires_at', models.DateTimeField()),
            ],
        ),
    ]