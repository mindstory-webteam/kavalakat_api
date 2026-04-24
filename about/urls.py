from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AboutViewSet, StrengthViewSet, MilestoneViewSet, ProjectViewSet, GalleryViewSet
router = DefaultRouter()
router.register(r'about',      AboutViewSet,     basename='about')
router.register(r'strengths',  StrengthViewSet,  basename='strength')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'projects',   ProjectViewSet,   basename='project')
router.register(r'gallery',    GalleryViewSet,   basename='gallery')
urlpatterns = [path('', include(router.urls))]
