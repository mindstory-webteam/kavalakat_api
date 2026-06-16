from django.contrib import admin
from django.utils.html import format_html

from .models import BranchLocation


@admin.register(BranchLocation)
class BranchLocationAdmin(admin.ModelAdmin):
    list_display = [
        'image_thumb', 'branch_name', 'phone_number', 'email',
        'status', 'created_at',
    ]
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['branch_name', 'address', 'phone_number', 'email']
    ordering = ['branch_name']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    date_hierarchy = 'created_at'
    actions = ['mark_active', 'mark_inactive']

    fieldsets = (
        ('Branch Details', {'fields': ('branch_name', 'address', 'phone_number', 'email')}),
        ('Map', {'fields': ('google_map_link',)}),
        ('Image', {'fields': ('location_image', 'image_preview')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def image_thumb(self, obj):
        if obj.location_image:
            return format_html(
                '<img src="{}" style="width:42px;height:42px;object-fit:cover;border-radius:6px;" />',
                obj.location_image.url,
            )
        return format_html('<span style="color:#999;">No image</span>')
    image_thumb.short_description = 'Image'

    def image_preview(self, obj):
        if obj.location_image:
            return format_html(
                '<img src="{}" style="max-width:320px;max-height:200px;object-fit:cover;border-radius:8px;" />',
                obj.location_image.url,
            )
        return 'No image uploaded.'
    image_preview.short_description = 'Preview'

    @admin.action(description='Mark selected branches as Active')
    def mark_active(self, request, queryset):
        updated = queryset.update(status=BranchLocation.STATUS_ACTIVE)
        self.message_user(request, f'{updated} branch(es) marked as active.')

    @admin.action(description='Mark selected branches as Inactive')
    def mark_inactive(self, request, queryset):
        updated = queryset.update(status=BranchLocation.STATUS_INACTIVE)
        self.message_user(request, f'{updated} branch(es) marked as inactive.')
