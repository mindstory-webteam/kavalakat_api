"""
chat/serializers.py
"""
from rest_framework import serializers
from .models import ChatSession, ChatMessage


class MessageInputSerializer(serializers.Serializer):
    """Incoming payload from the React widget."""
    session_key = serializers.CharField(max_length=100)
    message     = serializers.CharField(max_length=2000)

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 1:
            raise serializers.ValidationError('Message cannot be empty.')
        return value

    def validate_session_key(self, value):
        return value.strip()[:100]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model  = ChatSession
        fields = ['id', 'session_key', 'created_at', 'updated_at', 'messages']
