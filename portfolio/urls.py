from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ItemViewSet, PortfolioPageView

router = DefaultRouter()
router.register(r'portfolio/categories', CategoryViewSet, basename='portfolio-category')
router.register(r'portfolio/items',      ItemViewSet,     basename='portfolio-item')

urlpatterns = [
    # Full portfolio page (Trading + Distribution + Services in one call)
    path('portfolio/page/', PortfolioPageView.as_view(), name='portfolio-page'),

    # Category & Item CRUD
    path('', include(router.urls)),
]
