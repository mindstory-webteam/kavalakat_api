from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Item


class ItemInline(admin.TabularInline):
    model   = Item
    extra   = 1
    fields  = ['name', 'description', 'image', 'is_featured', 'is_active', 'order']
    show_change_link = True
    ordering = ['order', 'name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'order', 'is_active', 'item_count']
    list_filter   = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['slug']
    inlines       = [ItemInline]
    ordering      = ['order', 'name']

    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'description', 'icon'),
        }),
        ('Settings', {
            'fields': ('is_active', 'order'),
        }),
    )

    def item_count(self, obj):
        count  = obj.items.count()
        active = obj.items.filter(is_active=True).count()
        return format_html(
            '<span style="font-weight:600;">{}</span>'
            '<span style="color:#6b7280;font-size:11px;"> ({} active)</span>',
            count, active
        )
    item_count.short_description = 'Items'

    actions = ['activate_categories', 'deactivate_categories']

    def activate_categories(self, request, qs):
        qs.update(is_active=True)
        self.message_user(request, f'{qs.count()} category/categories activated.')
    activate_categories.short_description = 'Activate selected'

    def deactivate_categories(self, request, qs):
        qs.update(is_active=False)
        self.message_user(request, f'{qs.count()} category/categories deactivated.')
    deactivate_categories.short_description = 'Deactivate selected'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'is_featured', 'is_active', 'order', 'image_thumb', 'created_at']
    list_filter   = ['category', 'is_featured', 'is_active']
    list_editable = ['order', 'is_featured', 'is_active']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    ordering      = ['category__order', 'order', 'name']

    fieldsets = (
        ('Item Details', {
            'fields': ('name', 'category', 'description', 'tags'),
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_active', 'order'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return '—'
    image_thumb.short_description = 'Image'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:160px;border-radius:8px;border:1px solid #ddd;"/>',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'

    actions = ['feature_items', 'unfeature_items', 'activate_items', 'deactivate_items']

    def feature_items(self, request, qs):
        qs.update(is_featured=True)
    feature_items.short_description = 'Mark selected as featured'

    def unfeature_items(self, request, qs):
        qs.update(is_featured=False)
    unfeature_items.short_description = 'Remove featured flag'

    def activate_items(self, request, qs):
        qs.update(is_active=True)
    activate_items.short_description = 'Activate selected'

    def deactivate_items(self, request, qs):
        qs.update(is_active=False)
    deactivate_items.short_description = 'Deactivate selected'