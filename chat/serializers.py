"""
chat/serializers.py
"""
import re
from rest_framework import serializers
from .models import ChatSession, ChatMessage, ChatLead


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


# ── NEW: Chat Lead ────────────────────────────────────────────────────────────
class ChatLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatLead
        fields = [
            'id', 'session_key', 'name', 'phone', 'email',
            'query', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']
        extra_kwargs     = {'session_key': {'required': False, 'allow_blank': True}}

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Please provide a valid name.')
        return value

    def validate_phone(self, value):
        value = re.sub(r'[\s\-]', '', value.strip())
        # Indian 10-digit mobile, with optional +91 / 91 / 0 prefix
        if not re.fullmatch(r'(\+91|91|0)?[6-9]\d{9}', value):
            raise serializers.ValidationError('Please provide a valid 10-digit mobile number.')
        return value

    def validate_query(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Query cannot be empty.')
        return value
