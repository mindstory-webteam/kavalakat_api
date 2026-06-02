"""
chat/migrations/0001_initial.py
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('session_key', models.CharField(db_index=True, max_length=120, unique=True)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('updated_at',  models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-updated_at']},
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('role',       models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=20)),
                ('content',    models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session',    models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='chat.chatsession',
                )),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='ChatbotFAQ',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('question',   models.CharField(max_length=500)),
                ('answer',     models.TextField()),
                ('keywords',   models.CharField(blank=True, max_length=500)),
                ('is_active',  models.BooleanField(default=True)),
                ('order',      models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['order', 'question'], 'verbose_name': 'Chatbot FAQ',
                     'verbose_name_plural': 'Chatbot FAQs'},
        ),
    ]
