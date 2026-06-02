"""
chat/admin.py
"""
from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatbotFAQ


class ChatMessageInline(admin.TabularInline):
    model           = ChatMessage
    extra           = 0
    readonly_fields = ['role', 'content', 'created_at']
    can_delete      = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display    = ['session_key', 'message_count', 'created_at', 'updated_at']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines         = [ChatMessageInline]
    ordering        = ['-updated_at']

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def has_add_permission(self, request):
        return False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display    = ['session', 'role', 'short_content', 'created_at']
    list_filter     = ['role']
    readonly_fields = ['session', 'role', 'content', 'created_at']
    ordering        = ['-created_at']

    def short_content(self, obj):
        return obj.content[:80]
    short_content.short_description = 'Content'

    def has_add_permission(self, request):
        return False


@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display  = ['question', 'keywords', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter   = ['is_active']
    search_fields = ['question', 'answer', 'keywords']
    ordering      = ['order', 'question']
    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'keywords', 'is_active', 'order')
        }),
        ('Help', {
            'classes': ('collapse',),
            'fields': (),
            'description': (
                'Keywords: comma-separated words that trigger this FAQ. '
                'e.g. "price,cost,rate,charge" — if user types any of these, '
                'this answer is shown. Leave blank to match the full question text.'
            )
        }),
    )
