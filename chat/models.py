"""
chat/models.py
Stores chat sessions and messages.
"""
from django.db import models


class ChatSession(models.Model):
    session_key = models.CharField(max_length=120, unique=True, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Session {self.session_key[:12]}'


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


class ChatbotFAQ(models.Model):
    """
    Admin-managed FAQ entries.
    Add questions and answers from Django Admin → Chat → FAQs.
    The chatbot will use these to answer user questions.
    """
    question   = models.CharField(max_length=500, help_text='e.g. What services do you offer?')
    answer     = models.TextField(help_text='The reply the chatbot will give.')
    keywords   = models.CharField(
        max_length=500, blank=True,
        help_text='Comma-separated trigger words e.g. service,offer,provide'
    )
    is_active  = models.BooleanField(default=True)
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'question']
        verbose_name     = 'Chatbot FAQ'
        verbose_name_plural = 'Chatbot FAQs'

    def __str__(self):
        return self.question[:80]

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]
