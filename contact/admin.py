from django.contrib import admin
from .models import Contact, ContactLocation, Career, JobApplication, Enquiry


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display    = ['email', 'phone', 'city', 'updated_at']
    readonly_fields = ['updated_at']


@admin.register(ContactLocation)
class ContactLocationAdmin(admin.ModelAdmin):
    list_display  = ['branch_name', 'phone_number', 'whatsapp', 'email',
                     'working_hours', 'display_order', 'status', 'created_at']
    list_filter   = ['status']
    list_editable = ['display_order', 'status']
    search_fields = ['branch_name', 'address', 'phone_number', 'email']
    ordering      = ['display_order', 'branch_name']
    readonly_fields = ['created_at', 'updated_at']
    actions       = ['mark_active', 'mark_inactive']

    fieldsets = (
        ('Branch Details', {'fields': ('branch_name', 'address', 'display_order')}),
        ('Contact',        {'fields': ('phone_number', 'whatsapp', 'email', 'working_hours')}),
        ('Map',            {'fields': ('google_map_link',)}),
        ('Status',         {'fields': ('status',)}),
        ('Timestamps',     {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.action(description='Mark selected as Active')
    def mark_active(self, request, qs):
        qs.update(status=ContactLocation.STATUS_ACTIVE)

    @admin.action(description='Mark selected as Inactive')
    def mark_inactive(self, request, qs):
        qs.update(status=ContactLocation.STATUS_INACTIVE)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display    = ['title', 'department', 'job_type', 'location', 'is_active', 'deadline']
    list_filter     = ['job_type', 'is_active']
    search_fields   = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display    = ['name', 'email', 'phone', 'career', 'status', 'created_at']
    list_filter     = ['status', 'career']
    search_fields   = ['name', 'email', 'phone']
    readonly_fields = ['ip_address', 'created_at', 'updated_at']


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display    = ['name', 'email', 'phone', 'status', 'created_at']
    list_filter     = ['status']
    search_fields   = ['name', 'email', 'phone', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message',
                       'terms_accepted', 'ip_address', 'created_at', 'updated_at']
    date_hierarchy  = 'created_at'
    actions         = ['mark_read', 'mark_replied', 'mark_closed']

    def mark_read(self, request, qs): qs.update(status='read')
    mark_read.short_description = 'Mark as Read'

    def mark_replied(self, request, qs): qs.update(status='replied')
    mark_replied.short_description = 'Mark as Replied'

    def mark_closed(self, request, qs): qs.update(status='closed')
    mark_closed.short_description = 'Mark as Closed'
