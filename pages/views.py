from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from kavalakat.permissions import IsAdminOrReadOnly
from .models import Page
from .serializers import PageSerializer

class PageViewSet(viewsets.ModelViewSet):
    serializer_class   = PageSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = 'slug'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['title','content']
    ordering_fields    = ['order','title','created_at']

    def get_queryset(self):
        qs = Page.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(), 'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True, 'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Page created.', 'data': self.get_serializer(obj).data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Page updated.', 'data': self.get_serializer(obj).data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(); t = obj.title; obj.delete()
        return Response({'success': True, 'message': f'Page "{t}" deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, slug=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})
