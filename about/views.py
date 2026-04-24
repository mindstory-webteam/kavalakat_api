from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from kavalakat.permissions import IsAdminOrReadOnly
from .models import About, Strength, Milestone, Project, Gallery
from .serializers import AboutSerializer, StrengthSerializer, MilestoneSerializer, ProjectSerializer, GallerySerializer

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

class AboutViewSet(viewsets.ModelViewSet):
    serializer_class = AboutSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = About.objects.all()
    def list(self, request, *args, **kwargs):
        obj = About.objects.first()
        return Response({'success': True, 'data': self.get_serializer(obj).data if obj else None})
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs): return crud_create(self, request)
    def update(self, request, *args, **kwargs): return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs): return crud_destroy(self, request)

class StrengthViewSet(viewsets.ModelViewSet):
    serializer_class = StrengthSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title','description']
    ordering_fields = ['order','title']
    def get_queryset(self):
        qs = Strength.objects.all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(is_active=True)
        return qs
    def list(self, request, *args, **kwargs): return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs): return crud_create(self, request)
    def update(self, request, *args, **kwargs): return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs): return crud_destroy(self, request)
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object(); obj.is_active = not obj.is_active; obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})

class MilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = MilestoneSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Milestone.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['year','order']
    def list(self, request, *args, **kwargs): return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs): return crud_create(self, request)
    def update(self, request, *args, **kwargs): return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs): return crud_destroy(self, request)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured','year']
    search_fields = ['title','description','client','location']
    ordering_fields = ['created_at','year']
    def get_queryset(self): return Project.objects.all()
    def list(self, request, *args, **kwargs): return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs): return crud_create(self, request)
    def update(self, request, *args, **kwargs): return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs): return crud_destroy(self, request)
    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        obj = self.get_object(); obj.is_featured = not obj.is_featured; obj.save(update_fields=['is_featured'])
        return Response({'success': True, 'is_featured': obj.is_featured})

class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = GallerySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['order','created_at']
    def get_queryset(self):
        qs = Gallery.objects.all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(is_active=True)
        return qs
    def list(self, request, *args, **kwargs): return crud_list(self, request)
    def retrieve(self, request, *args, **kwargs): return crud_retrieve(self, request)
    def create(self, request, *args, **kwargs): return crud_create(self, request)
    def update(self, request, *args, **kwargs): return crud_update(self, request, kwargs.pop('partial', False))
    def destroy(self, request, *args, **kwargs): return crud_destroy(self, request)
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object(); obj.is_active = not obj.is_active; obj.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': obj.is_active})
