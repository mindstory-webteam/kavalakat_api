from django.contrib import admin
from .models import (
    ServiceCategory,
    ServiceAbout, ServiceCounter, ServiceOffer,
    ServiceFeatureSection, ServiceFeature,
    ServiceHighlight, ServiceLocation, ServiceNearbyPlace, Service,
)

admin.site.register(ServiceCategory)
admin.site.register(ServiceAbout)
admin.site.register(ServiceCounter)
admin.site.register(ServiceOffer)
admin.site.register(ServiceFeatureSection)
admin.site.register(ServiceFeature)
admin.site.register(ServiceHighlight)
admin.site.register(ServiceLocation)
admin.site.register(ServiceNearbyPlace)
admin.site.register(Service)
