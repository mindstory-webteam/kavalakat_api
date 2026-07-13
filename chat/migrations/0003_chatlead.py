# Generated migration — adds the ChatLead table.
# Place in chat/migrations/0003_chatlead.py then run:  python manage.py migrate chat
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatbotfaq_alter_chatsession_session_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, help_text='Chat session this lead was captured in.', max_length=120)),
                ('name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('query', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('resolved', 'Resolved')], default='pending', max_length=20)),
                ('admin_note', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Chatbot Lead',
                'verbose_name_plural': 'Chatbot Leads',
                'ordering': ['-created_at'],
            },
        ),
    ]
