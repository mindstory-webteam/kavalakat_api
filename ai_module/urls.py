from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenerateBlogView, AIGenerationLogViewSet
router = DefaultRouter()
router.register(r'ai/logs', AIGenerationLogViewSet, basename='ai-log')
urlpatterns = [
    path('ai/generate-blog/', GenerateBlogView.as_view(), name='ai-generate-blog'),
    path('', include(router.urls)),
]
