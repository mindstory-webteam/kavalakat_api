"""
chat/models.py
Stores every conversation session + individual messages.
"""
from django.db import models


class ChatSession(models.Model):
    """One browser session = one chat thread."""
    session_key  = models.CharField(max_length=100, unique=True, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Session {self.session_key[:12]}…'


class ChatMessage(models.Model):
    ROLE_USER      = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES   = [(ROLE_USER, 'User'), (ROLE_ASSISTANT, 'Assistant')]

    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.content[:60]}'
