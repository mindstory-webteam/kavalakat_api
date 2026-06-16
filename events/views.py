from django.db.models import Count, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from kavalakat.permissions import IsAdminOrReadOnly
from .models import Event, EventCategory, EventImage
from .serializers import (
    EventCategorySerializer, EventImageSerializer,
    EventListSerializer, EventSerializer,
)


# ── Event Category ────────────────────────────────────────────────────────────
class EventCategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/event-categories/                   list all categories
    POST   /api/event-categories/                   create  [admin]
    GET    /api/event-categories/{id}/              retrieve (+ events count)
    PUT    /api/event-categories/{id}/              update  [admin]
    PATCH  /api/event-categories/{id}/              partial [admin]
    DELETE /api/event-categories/{id}/              delete  [admin]
    POST   /api/event-categories/{id}/toggle-status/        [admin]
    GET    /api/event-categories/{id}/events/       list events in this category

    ?status=active|inactive  ?search=name|description  ?ordering=name|-created_at
    """
    serializer_class   = EventCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status']
    search_fields      = ['name', 'description']
    ordering_fields    = ['name', 'created_at', 'updated_at']
    ordering           = ['name']

    def get_queryset(self):
        qs = EventCategory.objects.all().annotate(event_count_annotated=Count('events'))
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status=EventCategory.STATUS_ACTIVE)
        return qs

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                         'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True,
                         'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Event category created.',
                         'data': self.get_serializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Event category updated.',
                         'data': self.get_serializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.name
        obj.delete()
        return Response({'success': True, 'message': f'"{name}" deleted.'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-status',
            permission_classes=[IsAdminOrReadOnly])
    def toggle_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = (
            EventCategory.STATUS_INACTIVE
            if obj.status == EventCategory.STATUS_ACTIVE
            else EventCategory.STATUS_ACTIVE
        )
        obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=True, methods=['get'], url_path='events')
    def events(self, request, pk=None):
        """
        GET /api/event-categories/{id}/events/
        Returns all published events belonging to this category.
        Supports ?upcoming=true  ?past=true  ?search=  ?ordering=
        """
        category = self.get_object()
        qs = (
            Event.objects
            .filter(category=category)
            .select_related('category')
            .prefetch_related(
                Prefetch('gallery_images',
                         queryset=EventImage.objects.order_by('order', 'uploaded_at'))
            )
        )
        if not (request.user and request.user.is_staff):
            qs = qs.filter(status=Event.STATUS_PUBLISHED)

        upcoming = request.query_params.get('upcoming', '').lower()
        if upcoming == 'true':
            qs = qs.filter(event_date__gte=timezone.now())

        past = request.query_params.get('past', '').lower()
        if past == 'true':
            qs = qs.filter(event_date__lt=timezone.now())

        search = request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(event_name__icontains=search) |
                Q(short_description__icontains=search) |
                Q(description__icontains=search)
            )

        qs = qs.order_by('-is_featured', '-event_date')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                EventListSerializer(page, many=True, context={'request': request}).data)
        return Response({
            'success':  True,
            'category': EventCategorySerializer(category, context={'request': request}).data,
            'count':    qs.count(),
            'data':     EventListSerializer(qs, many=True, context={'request': request}).data,
        })


# ── Event ─────────────────────────────────────────────────────────────────────
class EventViewSet(viewsets.ModelViewSet):
    """
    GET    /api/events/                  list (paginated, published only for public)
    POST   /api/events/                  create  [admin] multipart/form-data
    GET    /api/events/{id}/             retrieve full detail with gallery
    PUT    /api/events/{id}/             update  [admin]
    PATCH  /api/events/{id}/             partial [admin]
    DELETE /api/events/{id}/             delete  [admin]

    POST   /api/events/{id}/publish/            set status=published [admin]
    POST   /api/events/{id}/unpublish/          set status=draft [admin]
    POST   /api/events/{id}/toggle-status/      toggle draft/published [admin]
    GET    /api/events/{id}/images/             list gallery images
    POST   /api/events/{id}/add-image/          upload gallery image [admin] multipart
    DELETE /api/events/{id}/remove-image/{img}/ delete one gallery image [admin]

    Filters:
      ?category=<id>          by category FK
      ?status=draft|published
      ?is_featured=true|false
      ?upcoming=true          event_date >= now
      ?past=true              event_date < now
      ?search=keyword         event_name, short_description, description,
                              tag, organizer, venue, location
      ?ordering=-event_date | -created_at | event_name | is_featured
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'status', 'is_featured']
    search_fields      = ['event_name', 'short_description', 'description',
                          'tag', 'organizer', 'venue', 'location']
    ordering_fields    = ['event_date', 'created_at', 'event_name', 'is_featured']
    ordering           = ['-is_featured', '-event_date']

    def get_queryset(self):
        qs = (
            Event.objects
            .select_related('category')
            .prefetch_related(
                Prefetch('gallery_images',
                         queryset=EventImage.objects.order_by('order', 'uploaded_at'))
            )
        )
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status=Event.STATUS_PUBLISHED)

        upcoming = self.request.query_params.get('upcoming', '').lower()
        if upcoming == 'true':
            qs = qs.filter(event_date__gte=timezone.now())

        past = self.request.query_params.get('past', '').lower()
        if past == 'true':
            qs = qs.filter(event_date__lt=timezone.now())

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                         'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True,
                         'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Event created.',
                         'data': EventSerializer(obj, context={'request': request}).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Event updated.',
                         'data': EventSerializer(obj, context={'request': request}).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.event_name
        obj.delete()
        return Response({'success': True, 'message': f'"{name}" deleted.'},
                        status=status.HTTP_200_OK)

    # ── Status actions ────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='publish',
            permission_classes=[IsAdminOrReadOnly])
    def publish(self, request, pk=None):
        obj = self.get_object()
        obj.status = Event.STATUS_PUBLISHED
        obj.save(update_fields=['status'])
        return Response({'success': True, 'message': f'"{obj.event_name}" published.',
                         'status': obj.status})

    @action(detail=True, methods=['post'], url_path='unpublish',
            permission_classes=[IsAdminOrReadOnly])
    def unpublish(self, request, pk=None):
        obj = self.get_object()
        obj.status = Event.STATUS_DRAFT
        obj.save(update_fields=['status'])
        return Response({'success': True, 'message': f'"{obj.event_name}" set to draft.',
                         'status': obj.status})

    @action(detail=True, methods=['post'], url_path='toggle-status',
            permission_classes=[IsAdminOrReadOnly])
    def toggle_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = (
            Event.STATUS_DRAFT
            if obj.status == Event.STATUS_PUBLISHED
            else Event.STATUS_PUBLISHED
        )
        obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    # ── Gallery actions ───────────────────────────────────────────────────────
    @action(detail=True, methods=['get'], url_path='images')
    def images(self, request, pk=None):
        """GET /api/events/{id}/images/ — list all gallery images."""
        event = self.get_object()
        imgs  = event.gallery_images.all()
        return Response({'success': True, 'count': imgs.count(),
                         'data': EventImageSerializer(imgs, many=True,
                                                      context={'request': request}).data})

    @action(detail=True, methods=['post'], url_path='add-image',
            permission_classes=[IsAdminUser],
            parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def add_image(self, request, pk=None):
        """
        POST /api/events/{id}/add-image/
        Form fields:  image (file, required) | caption | order
        """
        event = self.get_object()
        ser   = EventImageSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        img = ser.save(event=event)
        return Response({'success': True, 'message': 'Image added.',
                         'data': EventImageSerializer(img, context={'request': request}).data},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            url_path=r'remove-image/(?P<img_id>\d+)',
            permission_classes=[IsAdminUser])
    def remove_image(self, request, pk=None, img_id=None):
        """DELETE /api/events/{id}/remove-image/{img_id}/"""
        event = self.get_object()
        try:
            img = event.gallery_images.get(pk=img_id)
        except EventImage.DoesNotExist:
            return Response({'success': False, 'message': 'Image not found.'},
                            status=status.HTTP_404_NOT_FOUND)
        img.delete()
        return Response({'success': True, 'message': 'Image removed.'},
                        status=status.HTTP_200_OK)
