"""
portfolio/views.py  — FIXED PortfolioPageView  (replace lines ~22-55 only)
──────────────────────────────────────────────────────────────────────────────
ROOT CAUSE:
    The old get() method called get_items() three times with the hardcoded
    strings 'Trading', 'Distribution', 'Services'.
    Any category created in the CMS that doesn't match one of those three
    exact names (e.g. "NEW TEST", "Logistics", "Exports") was silently ignored.

FIX:
    Loop over ALL active categories from the database.
    Use cat.slug as the response key (e.g. "new-test", "trading", "logistics").
    The response shape now matches whatever categories exist in the CMS,
    so you never need to touch this file again when adding a new category.

OLD response (hardcoded):
    {
        "trading":      [...],
        "distribution": [...],
        "services":     [...]
    }

NEW response (dynamic — includes every active category):
    {
        "trading":      [...],
        "distribution": [...],
        "services":     [...],
        "new-test":     [...]     ← appears automatically now
    }

NOTE: The rest of views.py (CategoryViewSet, ItemViewSet) is unchanged.
      Replace only the PortfolioPageView class below.
"""

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
    CategorySerializer,
    CategoryListSerializer,
    ItemSerializer,
    ItemListSerializer,
)


# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO PAGE — FIXED: dynamic loop replaces 3 hardcoded keys
# ─────────────────────────────────────────────────────────────────────────────

class PortfolioPageView(APIView):
    """
    GET /api/portfolio/page/

    Returns ALL active categories and their items in one API call.
    The response keys are derived from each category's slug,
    so adding a new category in the CMS automatically adds it here.

    Response:
    {
        "success": true,
        "data": {
            "trading":      [ {id, name, hero_title, banner_image_url, ...}, ... ],
            "distribution": [ ... ],
            "services":     [ ... ],
            "new-test":     [ ... ]   ← any new category appears here automatically
        }
    }

    NOTE: Use GET /api/portfolio/items/{id}/ for FULL detail
          including features[], brands[], testimonials[].
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # ── FIXED: loop over all active categories instead of 3 hardcoded names ──
        categories = Category.objects.filter(is_active=True).order_by('order', 'name')

        data = {}
        for cat in categories:
            items = cat.items.filter(is_active=True).order_by('order', 'name')
            data[cat.slug] = ItemListSerializer(
                items, many=True, context={'request': request}
            ).data

        return Response({'success': True, 'data': data})


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY VIEWSET  (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field       = 'name'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['order', 'name']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'create', 'update', 'partial_update'):
            return CategorySerializer
        return CategoryListSerializer

    def get_queryset(self):
        qs = Category.objects.prefetch_related('items').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def list(self, request, *args, **kwargs):
        qs   = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                CategoryListSerializer(page, many=True, context={'request': request}).data
            )
        return Response({
            'success': True,
            'count':   qs.count(),
            'data':    CategoryListSerializer(qs, many=True, context={'request': request}).data,
        })

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('name', '')
        try:
            obj = Category.objects.prefetch_related('items').get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        if not (request.user and request.user.is_staff):
            if not obj.is_active:
                raise NotFound(f"Category '{name}' not found.")
        return Response({
            'success': True,
            'data':    CategorySerializer(obj, context={'request': request}).data,
        })

    def create(self, request, *args, **kwargs):
        s = CategorySerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" created.',
            'data':    CategorySerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        name    = kwargs.get('name', '')
        try:
            obj = Category.objects.get(name__iexact=name)
        except Category.DoesNotExist:
            raise NotFound(f"Category '{name}' not found.")
        s = CategorySerializer(obj, data=request.data, partial=partial,
                               context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Category "{obj.name}" updated.',
            'data':    CategorySerializer(obj, context={'request': request}).data,
        })

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

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, name=None):
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


# ─────────────────────────────────────────────────────────────────────────────
# ITEM VIEWSET  (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'category__name', 'category__slug',
                          'is_featured', 'is_active']
    search_fields      = ['name', 'description', 'tags', 'category__name',
                          'hero_title', 'about_title', 'about_description', 'brands_heading']
    ordering_fields    = ['order', 'created_at', 'name', 'category__order']

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        return ItemSerializer

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
            'count':   qs.count(),
            'data':    ItemListSerializer(qs, many=True, context={'request': request}).data,
        })

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response({
            'success': True,
            'data':    ItemSerializer(obj, context={'request': request}).data,
        })

    def create(self, request, *args, **kwargs):
        s = ItemSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" created.',
            'data':    ItemSerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = ItemSerializer(
            self.get_object(),
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" updated.',
            'data':    ItemSerializer(obj, context={'request': request}).data,
        })

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
        obj = self.get_object()
        obj.is_featured = not obj.is_featured
        obj.save(update_fields=['is_featured'])
        return Response({
            'success':     True,
            'message':     f'Item {"featured" if obj.is_featured else "unfeatured"}.',
            'is_featured': obj.is_featured,
        })

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({
            'success':   True,
            'message':   f'Item {"activated" if obj.is_active else "deactivated"}.',
            'is_active': obj.is_active,
        })
