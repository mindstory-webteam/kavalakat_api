from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventCategoryViewSet, EventViewSet

router = DefaultRouter()
router.register(r'event-categories', EventCategoryViewSet, basename='event-category')
router.register(r'events',           EventViewSet,         basename='event')

urlpatterns = [path('', include(router.urls))]
