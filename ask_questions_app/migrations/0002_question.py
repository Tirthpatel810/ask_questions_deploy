# Generated by Django 5.0 on 2024-10-20 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ask_questions_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]