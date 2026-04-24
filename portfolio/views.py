from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from kavalakat.permissions import IsAdminOrReadOnly
from .models import Category, Item
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    ItemSerializer, PortfolioPageSerializer,
)


class PortfolioPageView(APIView):
    """
    GET /api/portfolio/page/

    Returns the complete portfolio page layout in a single call —
    exactly matching the 3-column website design:

    {
        "success": true,
        "data": {
            "trading":      [ { id, name, ... }, ... ],
            "distribution": [ ... ],
            "services":     [ ... ]
        }
    }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        def get_items(cat_name):
            try:
                cat = Category.objects.get(name__iexact=cat_name, is_active=True)
                qs  = cat.items.filter(is_active=True).order_by('order', 'name')
                return ItemSerializer(qs, many=True, context={'request': request}).data
            except Category.DoesNotExist:
                return []

        return Response({
            'success': True,
            'data': {
                'trading':      get_items('Trading'),
                'distribution': get_items('Distribution'),
                'services':     get_items('Services'),
            }
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Portfolio Category CRUD

    Public:
        GET  /api/portfolio/categories/           list all active categories
        GET  /api/portfolio/categories/{name}/    category detail + all items

    Admin (JWT required):
        POST   /api/portfolio/categories/           create category
        PUT    /api/portfolio/categories/{name}/    update
        PATCH  /api/portfolio/categories/{name}/    partial update
        DELETE /api/portfolio/categories/{name}/    delete
        POST   /api/portfolio/categories/{name}/toggle-active/

    Filters & search:
        ?is_active=true
        ?search=trading
    """
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = 'name'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name', 'created_at']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return CategorySerializer
        return CategoryListSerializer

    def get_queryset(self):
        qs = Category.objects.prefetch_related('items').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    # ── List ──────────────────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                CategoryListSerializer(page, many=True, context={'request': request}).data
            )
        return Response({
            'success': True,
            'count': qs.count(),
            'data': CategoryListSerializer(qs, many=True, context={'request': request}).data,
        })

    # ── Retrieve ──────────────────────────────────────────────────────────────
    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('name', '')
        try:
            obj = Category.objects.prefetch_related('items').get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        # Public users: only show active items
        if not (request.user and request.user.is_staff):
            if not obj.is_active:
                raise NotFound(f"Category '{name}' not found.")
        return Response({
            'success': True,
            'data': CategorySerializer(obj, context={'request': request}).data,
        })

    # ── Create ────────────────────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        s = CategorySerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" created.',
            'data': CategorySerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        name    = kwargs.get('name', '')
        try:
            obj = Category.objects.get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        s = CategorySerializer(obj, data=request.data, partial=partial, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" updated.',
            'data': CategorySerializer(obj, context={'request': request}).data,
        })

    # ── Destroy ───────────────────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        name = kwargs.get('name', '')
        try:
            obj = Category.objects.get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        n = obj.name
        obj.delete()
        return Response({
            'success': True,
            'message': f'Category "{n}" and all its items deleted.',
        }, status=status.HTTP_200_OK)

    # ── Custom actions ────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, name=None):
        """POST /api/portfolio/categories/{name}/toggle-active/"""
        try:
            obj = Category.objects.get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        state = 'activated' if obj.is_active else 'deactivated'
        return Response({
            'success':   True,
            'message':   f'Category "{obj.name}" {state}.',
            'is_active': obj.is_active,
        })


class ItemViewSet(viewsets.ModelViewSet):
    """
    Portfolio Item CRUD

    Public:
        GET  /api/portfolio/items/                    all active items
        GET  /api/portfolio/items/{id}/               item detail
        GET  /api/portfolio/items/?category__name=Trading
        GET  /api/portfolio/items/?is_featured=true
        GET  /api/portfolio/items/?search=cement

    Admin (JWT required):
        POST   /api/portfolio/items/         create
        PUT    /api/portfolio/items/{id}/    full update
        PATCH  /api/portfolio/items/{id}/    partial update
        DELETE /api/portfolio/items/{id}/    delete
        POST   /api/portfolio/items/{id}/toggle-featured/
        POST   /api/portfolio/items/{id}/toggle-active/
    """
    serializer_class   = ItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'category__name', 'category__slug',
                          'is_featured', 'is_active']
    search_fields      = ['name', 'description', 'tags', 'category__name']
    ordering_fields    = ['order', 'created_at', 'name', 'category__order']

    def get_queryset(self):
        qs = Item.objects.select_related('category').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True, category__is_active=True)
        return qs

    # ── List ──────────────────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response({
            'success': True,
            'count': qs.count(),
            'data': self.get_serializer(qs, many=True).data,
        })

    # ── Retrieve ──────────────────────────────────────────────────────────────
    def retrieve(self, request, *args, **kwargs):
        return Response({
            'success': True,
            'data': self.get_serializer(self.get_object()).data,
        })

    # ── Create ────────────────────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" created.',
            'data': self.get_serializer(obj).data,
        }, status=status.HTTP_201_CREATED)

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(
            self.get_object(), data=request.data, partial=partial
        )
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" updated.',
            'data': self.get_serializer(obj).data,
        })

    # ── Destroy ───────────────────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        n   = obj.name
        obj.delete()
        return Response({
            'success': True,
            'message': f'Item "{n}" deleted.',
        }, status=status.HTTP_200_OK)

    # ── Custom actions ────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        """POST /api/portfolio/items/{id}/toggle-featured/"""
        obj = self.get_object()
        obj.is_featured = not obj.is_featured
        obj.save(update_fields=['is_featured'])
        return Response({
            'success':    True,
            'message':    f'Item "{"un" if not obj.is_featured else ""}featured".',
            'is_featured': obj.is_featured,
        })

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """POST /api/portfolio/items/{id}/toggle-active/"""
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({
            'success':   True,
            'message':   f'Item "{"activated" if obj.is_active else "deactivated"}".',
            'is_active': obj.is_active,
        })
