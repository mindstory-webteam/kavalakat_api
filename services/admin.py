from django.contrib import admin
from .models import (
    ServiceCategory, Service, ServiceAbout, ServiceCounter, ServiceOffer,
    ServiceFeatureSection, ServiceFeature, ServiceHighlight, ServiceLocation, ServiceNearbyPlace,
)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'color', 'order', 'is_active']
    list_editable       = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display        = ['name', 'category', 'is_active', 'is_featured', 'order']
    list_editable       = ['order', 'is_active', 'is_featured']
    list_filter         = ['category', 'is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(ServiceAbout)
admin.site.register(ServiceCounter)
admin.site.register(ServiceOffer)
admin.site.register(ServiceFeatureSection)
admin.site.register(ServiceFeature)
admin.site.register(ServiceHighlight)
admin.site.register(ServiceLocation)
admin.site.register(ServiceNearbyPlace)
