"""
chat/serializers.py
"""
from rest_framework import serializers
from .models import ChatSession, ChatMessage


class MessageInputSerializer(serializers.Serializer):
    session_key = serializers.CharField(max_length=120)
    message     = serializers.CharField(max_length=2000)

    def validate_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Message cannot be empty.')
        return value

    def validate_session_key(self, value):
        return value.strip()[:120]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages      = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model  = ChatSession
        fields = ['id', 'session_key', 'message_count', 'created_at', 'updated_at', 'messages']

    def get_message_count(self, obj):
        return obj.messages.count()
