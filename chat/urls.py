"""
chat/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatView, ChatSessionViewSet

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionViewSet, basename='chat-session')

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('', include(router.urls)),
]
