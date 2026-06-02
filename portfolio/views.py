"""
portfolio/views.py
──────────────────────────────────────────────────────────────────────────────
FIX SUMMARY
───────────
1. PortfolioPageView  — DYNAMIC: loops all active categories instead of
   3 hardcoded names (trading / distribution / services).
   New categories created in the CMS appear automatically in the API.

2. CategoryViewSet    — FIXED lookup_field: uses pk (integer) not name,
   so GET /api/portfolio/categories/5/ works correctly.
   Slug-based lookup also supported via /api/portfolio/categories/?slug=...
   filter.

3. ItemViewSet        — unchanged, fully functional.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from kavalakat.permissions import IsAdminOrReadOnly
from .models import Category, Item
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    ItemSerializer,
    ItemListSerializer,
)


# ─── PORTFOLIO PAGE ───────────────────────────────────────────────────────────

class PortfolioPageView(APIView):
    """
    GET /api/portfolio/page/

    Returns ALL active categories and their items in one API call.
    Keys are each category's slug — completely dynamic, no hardcoding.

    Response shape:
    {
        "success": true,
        "data": {
            "trading":      [ {id, name, ...}, ... ],
            "distribution": [ ... ],
            "services":     [ ... ],
            "test-new":     [ ... ]   ← any new category appears here automatically
        },
        "categories": [
            {"id": 1, "name": "Trading", "slug": "trading", "item_count": 5},
            ...
        ]
    }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = (
            Category.objects
            .filter(is_active=True)
            .prefetch_related('items')
            .order_by('order', 'name')
        )

        items_by_category = {}
        for cat in categories:
            active_items = cat.items.filter(is_active=True).order_by('order', 'name')
            items_by_category[cat.slug] = ItemListSerializer(
                active_items,
                many=True,
                context={'request': request},
            ).data

        return Response({
            'success'   : True,
            'data'      : items_by_category,
            # also expose category meta so frontend can build navigation dynamically
            'categories': CategoryListSerializer(categories, many=True).data,
        })


# ─── CATEGORY VIEWSET ─────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/portfolio/categories/          → list all categories
    POST   /api/portfolio/categories/          → create (admin)
    GET    /api/portfolio/categories/<pk>/     → retrieve by ID   ← FIXED
    PUT    /api/portfolio/categories/<pk>/     → update (admin)
    PATCH  /api/portfolio/categories/<pk>/     → partial update (admin)
    DELETE /api/portfolio/categories/<pk>/     → delete (admin)

    Filter by slug:  /api/portfolio/categories/?slug=trading
    Filter active:   /api/portfolio/categories/?is_active=true
    """
    permission_classes = [IsAdminOrReadOnly]
    # FIXED: was lookup_field='name' which broke /categories/<id>/ lookups
    # Now uses default pk so numeric IDs work correctly.
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'slug']
    search_fields    = ['name', 'description']
    ordering_fields  = ['order', 'name']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return CategorySerializer
        return CategoryListSerializer

    def get_queryset(self):
        qs = Category.objects.prefetch_related('items').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs.order_by('order', 'name')

    # ── list ──────────────────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                CategoryListSerializer(page, many=True, context={'request': request}).data
            )
        return Response({
            'success': True,
            'count'  : qs.count(),
            'data'   : CategoryListSerializer(qs, many=True, context={'request': request}).data,
        })

    # ── retrieve ──────────────────────────────────────────────────────────────
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response({
            'success': True,
            'data'   : CategorySerializer(obj, context={'request': request}).data,
        })

    # ── create ────────────────────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        s = CategorySerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" created.',
            'data'   : CategorySerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = CategorySerializer(
            self.get_object(),
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" updated.',
            'data'   : CategorySerializer(obj, context={'request': request}).data,
        })

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ── destroy ───────────────────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        obj  = self.get_object()
        name = obj.name
        obj.delete()
        return Response({
            'success': True,
            'message': f'Category "{name}" and all its items deleted.',
        }, status=status.HTTP_200_OK)

    # ── toggle-active ─────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj           = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        state = 'activated' if obj.is_active else 'deactivated'
        return Response({
            'success'  : True,
            'message'  : f'Category "{obj.name}" {state}.',
            'is_active': obj.is_active,
        })


# ─── ITEM VIEWSET ─────────────────────────────────────────────────────────────

class ItemViewSet(viewsets.ModelViewSet):
    """
    GET    /api/portfolio/items/          → list (lightweight)
    POST   /api/portfolio/items/          → create (admin)
    GET    /api/portfolio/items/<pk>/     → full detail
    PUT    /api/portfolio/items/<pk>/     → update (admin)
    PATCH  /api/portfolio/items/<pk>/     → partial update (admin)
    DELETE /api/portfolio/items/<pk>/     → delete (admin)

    Filter by category:  ?category=<id>  or  ?category__slug=trading
    Search:              ?search=cement
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'category__name', 'category__slug',
                          'is_featured', 'is_active']
    search_fields      = ['name', 'description', 'tags', 'category__name',
                          'hero_title', 'about_title', 'about_description', 'brands_heading']
    ordering_fields    = ['order', 'created_at', 'name', 'category__order']

    def get_serializer_class(self):
        return ItemListSerializer if self.action == 'list' else ItemSerializer

    def get_queryset(self):
        qs = Item.objects.select_related('category').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True, category__is_active=True)
        return qs

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ItemListSerializer(page, many=True, context={'request': request}).data
            )
        return Response({
            'success': True,
            'count'  : qs.count(),
            'data'   : ItemListSerializer(qs, many=True, context={'request': request}).data,
        })

    def retrieve(self, request, *args, **kwargs):
        return Response({
            'success': True,
            'data'   : ItemSerializer(self.get_object(), context={'request': request}).data,
        })

    def create(self, request, *args, **kwargs):
        s = ItemSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" created.',
            'data'   : ItemSerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = ItemSerializer(
            self.get_object(),
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" updated.',
            'data'   : ItemSerializer(obj, context={'request': request}).data,
        })

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        n   = obj.name
        obj.delete()
        return Response({
            'success': True,
            'message': f'Item "{n}" deleted.',
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        obj             = self.get_object()
        obj.is_featured = not obj.is_featured
        obj.save(update_fields=['is_featured'])
        return Response({
            'success'    : True,
            'message'    : f'Item {"featured" if obj.is_featured else "unfeatured"}.',
            'is_featured': obj.is_featured,
        })

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj           = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({
            'success'  : True,
            'message'  : f'Item {"activated" if obj.is_active else "deactivated"}.',
            'is_active': obj.is_active,
        })