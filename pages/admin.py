from django.contrib import admin
from django.utils.html import format_html
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ['title', 'slug', 'order', 'is_active', 'updated_at']
    list_filter   = ['is_active']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'created_at', 'updated_at']
    actions = ['activate', 'deactivate']
    def activate(self, request, qs): qs.update(is_active=True)
    activate.short_description = 'Activate selected'
    def deactivate(self, request, qs): qs.update(is_active=False)
    deactivate.short_description = 'Deactivate selected'
