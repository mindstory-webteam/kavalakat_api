from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from kavalakat.permissions import IsAdminOrReadOnly
from .models import Contact, ContactLocation, Career, JobApplication, Enquiry
from .serializers import (
    ContactSerializer, ContactLocationSerializer,
    CareerSerializer,
    JobApplicationPublicSerializer, JobApplicationAdminSerializer,
    EnquiryPublicSerializer, EnquiryAdminSerializer,
)


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


# ── Contact Info ──────────────────────────────────────────────────────────────
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class   = ContactSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset           = Contact.objects.all()

    def list(self, request, *args, **kwargs):
        obj = Contact.objects.first()
        return Response({'success': True,
                         'data': self.get_serializer(obj).data if obj else None})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True,
                         'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Created.',
                         'data': self.get_serializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Updated.',
                         'data': self.get_serializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success': True, 'message': 'Deleted.'}, status=status.HTTP_200_OK)


# ── Contact Locations ─────────────────────────────────────────────────────────
class ContactLocationViewSet(viewsets.ModelViewSet):
    """
    GET    /api/contact-locations/                  list all
    POST   /api/contact-locations/                  create [admin]
    GET    /api/contact-locations/{id}/             retrieve
    PUT    /api/contact-locations/{id}/             update [admin]
    PATCH  /api/contact-locations/{id}/             partial [admin]
    DELETE /api/contact-locations/{id}/             delete [admin]
    POST   /api/contact-locations/{id}/toggle-status/      [admin]

    ?status=active|inactive  ?search=branch_name|address|phone|email
    ?ordering=display_order|-created_at
    """
    serializer_class   = ContactLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status']
    search_fields      = ['branch_name', 'address', 'phone_number', 'email']
    ordering_fields    = ['display_order', 'branch_name', 'created_at']
    ordering           = ['display_order', 'branch_name']

    def get_queryset(self):
        qs = ContactLocation.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status=ContactLocation.STATUS_ACTIVE)
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
        return Response({'success': True, 'message': 'Location created.',
                         'data': self.get_serializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Location updated.',
                         'data': self.get_serializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.branch_name
        obj.delete()
        return Response({'success': True, 'message': f'"{name}" deleted.'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-status',
            permission_classes=[IsAdminOrReadOnly])
    def toggle_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = (
            ContactLocation.STATUS_INACTIVE
            if obj.status == ContactLocation.STATUS_ACTIVE
            else ContactLocation.STATUS_ACTIVE
        )
        obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})


# ── Career ────────────────────────────────────────────────────────────────────
class CareerViewSet(viewsets.ModelViewSet):
    serializer_class   = CareerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['job_type', 'is_active', 'department']
    search_fields      = ['title', 'description', 'location']
    ordering_fields    = ['created_at', 'title', 'deadline']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Career.objects.annotate(app_count=Count('applications'))
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                         'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True, 'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Career posted.',
                         'data': self.get_serializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Career updated.',
                         'data': self.get_serializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({'success': True, 'message': f'"{obj.title}" deleted.'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-active',
            permission_classes=[IsAdminOrReadOnly])
    def toggle_active(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})


# ── Job Application ───────────────────────────────────────────────────────────
class JobApplicationViewSet(viewsets.ModelViewSet):
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'career']
    search_fields    = ['name', 'email', 'phone']
    ordering_fields  = ['created_at']
    ordering         = ['-created_at']

    def get_queryset(self):
        return JobApplication.objects.select_related('career').all()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return JobApplicationAdminSerializer
        return JobApplicationPublicSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                         'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True, 'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = JobApplicationPublicSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save(ip_address=_get_ip(request))
        return Response({'success': True,
                         'message': 'Application submitted! We will get back to you.',
                         'data': JobApplicationPublicSerializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = JobApplicationAdminSerializer(
            self.get_object(), data=request.data, partial=partial,
            context=self.get_serializer_context())
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Application updated.',
                         'data': JobApplicationAdminSerializer(
                             obj, context=self.get_serializer_context()).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success': True, 'message': 'Deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def shortlist(self, request, pk=None):
        obj = self.get_object(); obj.status = 'shortlisted'; obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        obj = self.get_object(); obj.status = 'rejected'; obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def hire(self, request, pk=None):
        obj = self.get_object(); obj.status = 'hired'; obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        counts = {r['status']: r['count']
                  for r in JobApplication.objects.values('status').annotate(count=Count('id'))}
        return Response({'success': True, 'data': {
            s: counts.get(s, 0) for s in ['new','reviewed','shortlisted','rejected','hired']
        } | {'total': JobApplication.objects.count()}})


# ── Enquiry ───────────────────────────────────────────────────────────────────
class EnquiryViewSet(viewsets.ModelViewSet):
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields    = ['name', 'email', 'phone', 'subject', 'message']
    ordering_fields  = ['created_at']
    ordering         = ['-created_at']

    def get_queryset(self):
        return Enquiry.objects.all()

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_staff:
            return EnquiryAdminSerializer
        return EnquiryPublicSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                         'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == Enquiry.STATUS_NEW and request.user.is_staff:
            obj.status = Enquiry.STATUS_READ
            obj.save(update_fields=['status'])
        return Response({'success': True, 'data': self.get_serializer(obj).data})

    def create(self, request, *args, **kwargs):
        s = EnquiryPublicSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save(ip_address=_get_ip(request))
        return Response({'success': True,
                         'message': 'Thank you! We will get back to you within 24 hours.',
                         'data': EnquiryPublicSerializer(obj).data},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = EnquiryAdminSerializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Updated.',
                         'data': EnquiryAdminSerializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success': True, 'message': 'Deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-replied', permission_classes=[IsAdminUser])
    def mark_replied(self, request, pk=None):
        obj = self.get_object(); obj.status = 'replied'; obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=True, methods=['post'], url_path='mark-closed', permission_classes=[IsAdminUser])
    def mark_closed(self, request, pk=None):
        obj = self.get_object(); obj.status = 'closed'; obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        counts = {r['status']: r['count']
                  for r in Enquiry.objects.values('status').annotate(count=Count('id'))}
        return Response({'success': True, 'data': {
            s: counts.get(s, 0) for s in ['new','read','replied','closed']
        } | {'total': Enquiry.objects.count()}})
