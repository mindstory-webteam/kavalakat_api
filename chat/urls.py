"""
chat/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatView, ChatSessionViewSet, LeadCreateView, LeadViewSet

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'chat/leads/manage', LeadViewSet, basename='chat-lead-manage')

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat/leads/', LeadCreateView.as_view(), name='chat-lead-create'),
    path('', include(router.urls)),
]
