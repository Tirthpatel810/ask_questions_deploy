# Generated by Django 5.0 on 2024-10-20 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ask_questions_app', '0004_question_answers_question_source_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answers',
            field=models.JSONField(default={'title': 'None'}),
        ),
    ]
