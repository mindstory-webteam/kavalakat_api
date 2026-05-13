# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import (
#     CategoryViewSet, ItemViewSet,
#     HeroBannerViewSet, ProductAboutViewSet, ProductFAQViewSet,
#     TrustedBrandViewSet, TestimonialViewSet,
#     PortfolioPageView, ProductDetailPageView,
# )

# router = DefaultRouter()
# router.register(r'portfolio/categories',   CategoryViewSet,     basename='portfolio-category')
# router.register(r'portfolio/items',        ItemViewSet,         basename='portfolio-item')
# router.register(r'portfolio/banners',      HeroBannerViewSet,   basename='portfolio-banner')
# router.register(r'portfolio/about',        ProductAboutViewSet, basename='portfolio-about')
# router.register(r'portfolio/faqs',         ProductFAQViewSet,   basename='portfolio-faq')
# router.register(r'portfolio/brands',       TrustedBrandViewSet, basename='portfolio-brand')
# router.register(r'portfolio/testimonials', TestimonialViewSet,  basename='portfolio-testimonial')

# urlpatterns = [
#     # REST API — all under /api/portfolio/...
#     path('api/portfolio/page/', PortfolioPageView.as_view(), name='portfolio-page'),
#     path('api/', include(router.urls)),

#     # Frontend page — /products/Steel/  /products/Cement/  etc.
#     path('products/<str:category_name>/', ProductDetailPageView.as_view(), name='product-detail'),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ItemViewSet, PortfolioPageView

router = DefaultRouter()
router.register(r'portfolio/categories', CategoryViewSet, basename='portfolio-category')
router.register(r'portfolio/items',      ItemViewSet,     basename='portfolio-item')

urlpatterns = [
    # Full 3-column portfolio page (recommended for frontend)
    path('portfolio/page/', PortfolioPageView.as_view(), name='portfolio-page'),
    path('', include(router.urls)),
]
