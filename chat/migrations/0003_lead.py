# Generated for Lead capture feature

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatbotfaq_alter_chatsession_session_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('query', models.TextField(help_text='What the visitor asked / was interested in.')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('resolved', 'Resolved')], default='pending', max_length=20)),
                ('source', models.CharField(default='chatbot', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads', to='chat.chatsession')),
            ],
            options={
                'verbose_name': 'Chatbot Lead',
                'verbose_name_plural': 'Chatbot Leads',
                'ordering': ['-created_at'],
            },
        ),
    ]
