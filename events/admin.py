from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventCategory, EventImage


class EventImageInline(admin.TabularInline):
    model           = EventImage
    extra           = 1
    fields          = ['preview', 'image', 'caption', 'order']
    readonly_fields = ['preview']
    ordering        = ['order', 'uploaded_at']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:60px;height:44px;object-fit:cover;border-radius:4px;"/>',
                               obj.image.url)
        return '—'
    preview.short_description = '▶'


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display    = ['name', 'slug', 'status', 'icon', 'event_count', 'created_at']
    list_filter     = ['status']
    list_editable   = ['status']
    search_fields   = ['name', 'description']
    ordering        = ['name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    actions         = ['mark_active', 'mark_inactive']

    fieldsets = (
        ('Details',    {'fields': ('name', 'slug', 'description', 'icon')}),
        ('Status',     {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def event_count(self, obj):
        total = obj.events.count()
        pub   = obj.events.filter(status=Event.STATUS_PUBLISHED).count()
        return format_html('<b>{}</b> <span style="color:#999">({} published)</span>', total, pub)
    event_count.short_description = 'Events'

    @admin.action(description='Mark selected as Active')
    def mark_active(self, request, qs): qs.update(status=EventCategory.STATUS_ACTIVE)

    @admin.action(description='Mark selected as Inactive')
    def mark_inactive(self, request, qs): qs.update(status=EventCategory.STATUS_INACTIVE)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display        = ['thumb', 'event_name', 'category', 'tag', 'event_date',
                           'is_featured', 'status', 'created_at']
    list_filter         = ['status', 'is_featured', 'category', 'event_date']
    list_editable       = ['status', 'is_featured']
    list_select_related = ['category']
    search_fields       = ['event_name', 'short_description', 'description',
                           'organizer', 'tag', 'venue', 'location']
    ordering            = ['-is_featured', '-event_date']
    date_hierarchy      = 'event_date'
    readonly_fields     = ['slug', 'created_at', 'updated_at',
                           'featured_preview', 'logo_preview']
    inlines             = [EventImageInline]
    actions             = ['publish', 'unpublish', 'mark_featured', 'unmark_featured']

    fieldsets = (
        ('Event Details', {'fields': (
            'event_name', 'slug', 'category', 'tag',
            'short_description', 'description', 'is_featured',
        )}),
        ('Schedule & Venue', {'fields': (
            'event_date', 'event_time', 'venue', 'location',
        )}),
        ('Organiser', {'fields': ('organizer', 'organizer_logo', 'logo_preview')}),
        ('Featured Image', {'fields': ('featured_image', 'featured_preview')}),
        ('Registration',   {'fields': ('registration_url',)}),
        ('Status',         {'fields': ('status',)}),
        ('Timestamps',     {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def thumb(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width:42px;height:30px;object-fit:cover;border-radius:3px;"/>', obj.featured_image.url)
        return '—'
    thumb.short_description = ''

    def featured_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="max-width:340px;max-height:200px;object-fit:cover;border-radius:6px;"/>', obj.featured_image.url)
        return 'No image.'
    featured_preview.short_description = 'Preview'

    def logo_preview(self, obj):
        if obj.organizer_logo:
            return format_html('<img src="{}" style="max-width:120px;max-height:80px;object-fit:contain;border-radius:4px;"/>', obj.organizer_logo.url)
        return 'No logo.'
    logo_preview.short_description = 'Preview'

    @admin.action(description='Publish selected events')
    def publish(self, request, qs):
        n = qs.update(status=Event.STATUS_PUBLISHED)
        self.message_user(request, f'{n} event(s) published.')

    @admin.action(description='Set selected to Draft')
    def unpublish(self, request, qs):
        n = qs.update(status=Event.STATUS_DRAFT)
        self.message_user(request, f'{n} event(s) set to draft.')

    @admin.action(description='Mark as Featured')
    def mark_featured(self, request, qs): qs.update(is_featured=True)

    @admin.action(description='Remove Featured flag')
    def unmark_featured(self, request, qs): qs.update(is_featured=False)


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display  = ['preview_small', 'event', 'caption', 'order', 'uploaded_at']
    list_filter   = ['event__status']
    search_fields = ['event__event_name', 'caption']
    ordering      = ['event', 'order']
    raw_id_fields = ['event']
    readonly_fields = ['preview', 'uploaded_at']

    def preview_small(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:42px;height:30px;object-fit:cover;border-radius:3px;"/>', obj.image.url)
        return '—'
    preview_small.short_description = ''

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:340px;max-height:200px;object-fit:cover;border-radius:6px;"/>', obj.image.url)
        return 'No image.'
    preview.short_description = 'Preview'
