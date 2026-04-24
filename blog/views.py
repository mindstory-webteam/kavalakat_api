from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from kavalakat.permissions import IsAdminOrReadOnly
from .models import Category, Post
from .serializers import BlogCategorySerializer, PostListSerializer, PostDetailSerializer, PostWriteSerializer

class BlogCategoryViewSet(viewsets.ModelViewSet):
    serializer_class   = BlogCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = 'slug'
    queryset           = Category.objects.all()
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name','description']
    ordering_fields    = ['order','name']
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        return Response({'success': True, 'count': qs.count(), 'data': self.get_serializer(qs, many=True).data})
    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True, 'data': self.get_serializer(self.get_object()).data})
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data); s.is_valid(raise_exception=True); obj = s.save()
        return Response({'success': True, 'message': 'Category created.', 'data': self.get_serializer(obj).data}, status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial); s.is_valid(raise_exception=True); obj = s.save()
        return Response({'success': True, 'message': 'Category updated.', 'data': self.get_serializer(obj).data})
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(); n = obj.name; obj.delete()
        return Response({'success': True, 'message': f'Category "{n}" deleted.'}, status=status.HTTP_200_OK)

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = 'slug'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category__slug','category__name','status','is_featured','is_ai_generated','author']
    search_fields      = ['title','content','excerpt','tags']
    ordering_fields    = ['created_at','views','published_at','title']

    def get_queryset(self):
        qs = Post.objects.select_related('category','author').all()
        if not (self.request.user and self.request.user.is_staff): qs = qs.filter(status=Post.STATUS_PUBLISHED)
        return qs

    def get_serializer_class(self):
        if self.action in ('create','update','partial_update'): return PostWriteSerializer
        if self.action == 'retrieve': return PostDetailSerializer
        return PostListSerializer

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(PostListSerializer(page, many=True, context={'request': request}).data)
        return Response({'success': True, 'count': qs.count(), 'data': PostListSerializer(qs, many=True, context={'request': request}).data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object(); instance.increment_views()
        return Response({'success': True, 'data': PostDetailSerializer(instance, context={'request': request}).data})

    def create(self, request, *args, **kwargs):
        s = PostWriteSerializer(data=request.data, context={'request': request}); s.is_valid(raise_exception=True); obj = s.save()
        return Response({'success': True, 'message': 'Post created.', 'data': PostDetailSerializer(obj, context={'request': request}).data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = PostWriteSerializer(self.get_object(), data=request.data, partial=partial, context={'request': request})
        s.is_valid(raise_exception=True); obj = s.save()
        return Response({'success': True, 'message': 'Post updated.', 'data': PostDetailSerializer(obj, context={'request': request}).data})

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object(); t = obj.title; obj.delete()
        return Response({'success': True, 'message': f'Post "{t}" deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        post = self.get_object(); post.status = Post.STATUS_PUBLISHED
        post.published_at = post.published_at or timezone.now(); post.save(update_fields=['status','published_at'])
        return Response({'success': True, 'message': 'Post published.', 'data': PostListSerializer(post, context={'request': request}).data})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, slug=None):
        post = self.get_object(); post.status = Post.STATUS_DRAFT; post.save(update_fields=['status'])
        return Response({'success': True, 'message': 'Moved to draft.', 'data': PostListSerializer(post, context={'request': request}).data})

    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, slug=None):
        post = self.get_object(); post.is_featured = not post.is_featured; post.save(update_fields=['is_featured'])
        return Response({'success': True, 'is_featured': post.is_featured})

    @action(detail=False, methods=['get'], url_path=r'category/(?P<n>[^/.]+)')
    def by_category(self, request, name=None):
        try: cat = Category.objects.get(name__iexact=name)
        except Category.DoesNotExist: raise NotFound(f"Category '{name}' not found.")
        qs = self.get_queryset().filter(category=cat)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(PostListSerializer(page, many=True, context={'request': request}).data)
        return Response({'success': True, 'category': BlogCategorySerializer(cat).data, 'count': qs.count(), 'data': PostListSerializer(qs, many=True, context={'request': request}).data})

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(PostListSerializer(page, many=True, context={'request': request}).data)
        return Response({'success': True, 'count': qs.count(), 'data': PostListSerializer(qs, many=True, context={'request': request}).data})
