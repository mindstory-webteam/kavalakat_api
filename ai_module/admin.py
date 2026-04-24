from django.contrib import admin
from .models import AIGenerationLog

@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display  = ['topic_short','status','model_used','tokens_used','saved_as_post','requested_by','created_at']
    list_filter   = ['status','saved_as_post']
    search_fields = ['topic','generated_title','requested_by__username']
    readonly_fields = [f.name for f in AIGenerationLog._meta.get_fields() if hasattr(f,'name')]
    date_hierarchy = 'created_at'
    def topic_short(self, obj): return obj.topic[:60]+'…' if len(obj.topic)>60 else obj.topic
    topic_short.short_description = 'Topic'
    def has_add_permission(self, request): return False
