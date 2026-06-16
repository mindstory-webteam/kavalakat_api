from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactViewSet, ContactLocationViewSet,
    CareerViewSet, JobApplicationViewSet, EnquiryViewSet,
)

router = DefaultRouter()
router.register(r'contact',           ContactViewSet,         basename='contact')
router.register(r'contact-locations', ContactLocationViewSet, basename='contact-location')
router.register(r'careers',           CareerViewSet,          basename='career')
router.register(r'applications',      JobApplicationViewSet,  basename='application')
router.register(r'enquiry',           EnquiryViewSet,         basename='enquiry')

urlpatterns = [path('', include(router.urls))]
