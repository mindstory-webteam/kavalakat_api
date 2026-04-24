from django.contrib import admin
from .models import Contact, Career, Enquiry

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email','phone','city','updated_at']
    readonly_fields = ['updated_at']

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['title','department','job_type','location','is_active','deadline','created_at']
    list_filter  = ['job_type','is_active']
    search_fields = ['title','description']
    readonly_fields = ['created_at','updated_at']

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display  = ['name','email','enquiry_type','status','created_at']
    list_filter   = ['status','enquiry_type']
    search_fields = ['name','email','message']
    readonly_fields = ['name','email','phone','company','subject','message','enquiry_type','ip_address','created_at','updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_read','mark_replied','mark_closed']
    def mark_read(self, request, qs): qs.update(status=Enquiry.STATUS_READ)
    mark_read.short_description = 'Mark as Read'
    def mark_replied(self, request, qs): qs.update(status=Enquiry.STATUS_REPLIED)
    mark_replied.short_description = 'Mark as Replied'
    def mark_closed(self, request, qs): qs.update(status=Enquiry.STATUS_CLOSED)
    mark_closed.short_description = 'Mark as Closed'
