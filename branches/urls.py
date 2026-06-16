from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BranchLocationViewSet

router = DefaultRouter()
router.register(r'branches', BranchLocationViewSet, basename='branch')

urlpatterns = [path('', include(router.urls))]
