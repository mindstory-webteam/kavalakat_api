from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, CareerViewSet, EnquiryViewSet
router = DefaultRouter()
router.register(r'contact', ContactViewSet, basename='contact')
router.register(r'careers', CareerViewSet,  basename='career')
router.register(r'enquiry', EnquiryViewSet, basename='enquiry')
urlpatterns = [path('', include(router.urls))]
