"""
chat/serializers.py
"""
from rest_framework import serializers
from .models import ChatSession, ChatMessage, Lead


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


class LeadCreateSerializer(serializers.Serializer):
    """
    Used by the public chatbot widget to submit a lead.
    """
    session_key = serializers.CharField(max_length=120, required=False, allow_blank=True)
    name        = serializers.CharField(max_length=150)
    phone       = serializers.CharField(max_length=30, required=False, allow_blank=True)
    email       = serializers.EmailField(required=False, allow_blank=True)
    query       = serializers.CharField(max_length=2000, required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('phone') and not data.get('email'):
            raise serializers.ValidationError(
                'Please provide at least a phone number or an email address.'
            )
        return data

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Name is required.')
        return value


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lead
        fields = [
            'id', 'name', 'phone', 'email', 'query',
            'status', 'source', 'created_at', 'updated_at',
        ]
