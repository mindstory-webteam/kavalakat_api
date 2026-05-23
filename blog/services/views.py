from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from kavalakat.permissions import IsAdminOrReadOnly

from .models import (
    ServiceCategory, Service, ServiceAbout, ServiceCounter, ServiceOffer,
    ServiceFeatureSection, ServiceFeature,
    ServiceHighlight, ServiceLocation, ServiceNearbyPlace,
)
from .serializers import (
    ServiceCategorySerializer, ServiceSerializer, ServiceAboutSerializer, ServiceCounterSerializer,
    ServiceOfferSerializer, ServiceFeatureSectionSerializer, ServiceFeatureSerializer,
    ServiceHighlightSerializer, ServiceLocationSerializer, ServiceNearbyPlaceSerializer,
)


def crud_list(view, request):
    qs = view.filter_queryset(view.get_queryset())
    page = view.paginate_queryset(qs)
    if page is not None:
        return view.get_paginated_response(view.get_serializer(page, many=True).data)
    return Response({'success': True, 'count': qs.count(), 'data': view.get_serializer(qs, many=True).data})

def crud_retrieve(view, request, **kwargs):
    return Response({'success': True, 'data': view.get_serializer(view.get_object()).data})

def crud_create(view, request):
    s = view.get_serializer(data=request.data); s.is_valid(raise_exception=True); obj = s.save()
    return Response({'success': True, 'message': 'Created.', 'data': view.get_serializer(obj).data}, status=status.HTTP_201_CREATED)

def crud_update(view, request, partial=False):
    s = view.get_serializer(view.get_object(), data=request.data, partial=partial); s.is_valid(raise_exception=True); obj = s.save()
    return Response({'success': True, 'message': 'Updated.', 'data': view.get_serializer(obj).data})

def crud_destroy(view, request):
    view.get_object().delete()
    return Response({'success': True, 'message': 'Deleted.'}, status=status.HTTP_200_OK)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name']

    def get_queryset(self):
        qs = ServiceCategory.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active', 'is_featured']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name', 'created_at']

    def get_queryset(self):
        qs = Service.objects.prefetch_related('counters', 'offers', 'highlights').select_related('about', 'feature_section', 'location')
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object(); obj.is_active = not obj.is_active; obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})

    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        obj = self.get_object(); obj.is_featured = not obj.is_featured; obj.save(update_fields=['is_featured'])
        return Response({'success': True, 'is_featured': obj.is_featured})


class ServiceAboutViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceAboutSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    queryset           = ServiceAbout.objects.all()

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceCounterViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceCounterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['order', 'counter_title']

    def get_queryset(self):
        qs = ServiceCounter.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceOfferViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceOfferSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['order', 'offer_title']

    def get_queryset(self):
        qs = ServiceOffer.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceFeatureSectionViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceFeatureSectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    queryset           = ServiceFeatureSection.objects.prefetch_related('features').all()

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceFeatureViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceFeatureSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['section']
    ordering_fields    = ['order', 'feature_title']
    queryset           = ServiceFeature.objects.all()

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceHighlightViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceHighlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['display_order', 'highlight_title']

    def get_queryset(self):
        qs = ServiceHighlight.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceLocationViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    queryset           = ServiceLocation.objects.prefetch_related('nearby_places').all()

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)


class ServiceNearbyPlaceViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceNearbyPlaceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['location']
    ordering_fields    = ['order', 'nearby_place_name']
    queryset           = ServiceNearbyPlace.objects.all()

    def list(self, request, *args, **kwargs):    return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs):   return crud_create(self, request)
    def update(self, request, *args, **kwargs):   return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs):  return crud_destroy(self, request)
