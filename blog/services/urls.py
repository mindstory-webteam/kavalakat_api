from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCategoryViewSet, ServiceAboutViewSet, ServiceCounterViewSet, ServiceOfferViewSet,
    ServiceFeatureSectionViewSet, ServiceFeatureViewSet,
    ServiceHighlightViewSet, ServiceLocationViewSet, ServiceNearbyPlaceViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register(r'service-categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services',                  ServiceViewSet,               basename='service')
router.register(r'services-about',            ServiceAboutViewSet,          basename='service-about')
router.register(r'services-counters',         ServiceCounterViewSet,        basename='service-counter')
router.register(r'services-offers',           ServiceOfferViewSet,          basename='service-offer')
router.register(r'services-feature-sections', ServiceFeatureSectionViewSet, basename='service-feature-section')
router.register(r'services-features',         ServiceFeatureViewSet,        basename='service-feature')
router.register(r'services-highlights',       ServiceHighlightViewSet,      basename='service-highlight')
router.register(r'services-locations',        ServiceLocationViewSet,       basename='service-location')
router.register(r'services-nearby-places',    ServiceNearbyPlaceViewSet,    basename='service-nearby-place')

urlpatterns = [path('', include(router.urls))]
