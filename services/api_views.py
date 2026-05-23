from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from kavalakat.permissions import IsAdminOrReadOnly

from .models import (
    ServiceCategory, Service, ServiceAbout, ServiceCounter, ServiceOffer,
    ServiceFeatureSection, ServiceFeature, ServiceHighlight, ServiceLocation, ServiceNearbyPlace,
)
from .serializers import (
    ServiceCategorySerializer, ServiceListSerializer, ServiceSerializer,
    ServiceAboutSerializer, ServiceCounterSerializer, ServiceOfferSerializer,
    ServiceFeatureSectionSerializer, ServiceFeatureSerializer,
    ServiceHighlightSerializer, ServiceLocationSerializer, ServiceNearbyPlaceSerializer,
)


def ok_list(view, request):
    qs = view.filter_queryset(view.get_queryset())
    page = view.paginate_queryset(qs)
    if page is not None:
        return view.get_paginated_response(view.get_serializer(page, many=True).data)
    return Response({'success': True, 'count': qs.count(), 'data': view.get_serializer(qs, many=True).data})

def ok_retrieve(view):
    return Response({'success': True, 'data': view.get_serializer(view.get_object()).data})

def ok_create(view, request):
    s = view.get_serializer(data=request.data)
    s.is_valid(raise_exception=True)
    obj = s.save()
    return Response({'success': True, 'message': 'Created.', 'data': view.get_serializer(obj).data}, status=status.HTTP_201_CREATED)

def ok_update(view, request, partial=False):
    s = view.get_serializer(view.get_object(), data=request.data, partial=partial)
    s.is_valid(raise_exception=True)
    obj = s.save()
    return Response({'success': True, 'message': 'Updated.', 'data': view.get_serializer(obj).data})

def ok_delete(view):
    view.get_object().delete()
    return Response({'success': True, 'message': 'Deleted.'}, status=status.HTTP_200_OK)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name']
    ordering           = ['order', 'name']

    def get_queryset(self):
        qs = ServiceCategory.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active', 'is_featured', 'category']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name', 'created_at']
    ordering           = ['order', 'name']

    def get_queryset(self):
        qs = Service.objects.select_related('category').prefetch_related(
            'counters', 'offers', 'highlights', 'about',
            'feature_section', 'feature_section__features',
            'location', 'location__nearby_places',
        )
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        return ServiceListSerializer if self.action == 'list' else ServiceSerializer

    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)

    @action(detail=True, methods=['get'], url_path='full')
    def full(self, request, pk=None):
        return Response({'success': True, 'data': ServiceSerializer(self.get_object(), context=self.get_serializer_context()).data})

    @action(detail=True, methods=['post'], url_path='toggle-active', permission_classes=[IsAdminOrReadOnly])
    def toggle_active(self, request, pk=None):
        obj = self.get_object(); obj.is_active = not obj.is_active; obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})

    @action(detail=True, methods=['post'], url_path='toggle-featured', permission_classes=[IsAdminOrReadOnly])
    def toggle_featured(self, request, pk=None):
        obj = self.get_object(); obj.is_featured = not obj.is_featured; obj.save(update_fields=['is_featured'])
        return Response({'success': True, 'is_featured': obj.is_featured})


class ServiceAboutViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceAboutSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    def get_queryset(self): return ServiceAbout.objects.select_related('service').all()
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceCounterViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceCounterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['order']; ordering = ['order']
    def get_queryset(self):
        qs = ServiceCounter.objects.select_related('service').all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(is_active=True)
        return qs
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceOfferViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceOfferSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['order']; ordering = ['order']
    def get_queryset(self):
        qs = ServiceOffer.objects.select_related('service').all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(is_active=True)
        return qs
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceFeatureSectionViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceFeatureSectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    def get_queryset(self): return ServiceFeatureSection.objects.select_related('service').prefetch_related('features').all()
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceFeatureViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceFeatureSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['section']
    ordering_fields    = ['order']; ordering = ['order']
    def get_queryset(self): return ServiceFeature.objects.select_related('section__service').all()
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceHighlightViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceHighlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['service', 'is_active']
    ordering_fields    = ['display_order']; ordering = ['display_order']
    def get_queryset(self):
        qs = ServiceHighlight.objects.select_related('service').all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(is_active=True)
        return qs
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceLocationViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['service']
    def get_queryset(self): return ServiceLocation.objects.select_related('service').prefetch_related('nearby_places').all()
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)


class ServiceNearbyPlaceViewSet(viewsets.ModelViewSet):
    serializer_class   = ServiceNearbyPlaceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['location']
    ordering_fields    = ['order']; ordering = ['order']
    def get_queryset(self): return ServiceNearbyPlace.objects.select_related('location__service').all()
    def list(self, r, *a, **k):           return ok_list(self, r)
    def retrieve(self, r, *a, **k):       return ok_retrieve(self)
    def create(self, r, *a, **k):         return ok_create(self, r)
    def update(self, r, *a, **k):         return ok_update(self, r, partial=k.pop('partial', False))
    def partial_update(self, r, *a, **k): return ok_update(self, r, partial=True)
    def destroy(self, r, *a, **k):        return ok_delete(self)
