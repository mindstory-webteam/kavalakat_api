"""
chat/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatView, ChatLeadView, ChatLeadViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'chat/leads',    ChatLeadViewSet,    basename='chat-lead')

urlpatterns = [
    path('chat/',      ChatView.as_view(),     name='chat'),
    path('chat/lead/', ChatLeadView.as_view(), name='chat-lead-create'),
    path('', include(router.urls)),
]
