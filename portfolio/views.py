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
# PORTFOLIO PAGE — single API call returns all 3 columns
# ─────────────────────────────────────────────────────────────────────────────

class PortfolioPageView(APIView):
    """
    GET /api/portfolio/page/

    Returns the full 3-column portfolio layout in one API call.
    Each item includes hero_title, banner_image_url, about_title etc
    so the frontend can link to individual product detail pages.

    Response:
    {
        "success": true,
        "data": {
            "trading":      [ {id, name, hero_title, banner_image_url, ...}, ... ],
            "distribution": [ ... ],
            "services":     [ ... ]
        }
    }

    NOTE: Use GET /api/portfolio/items/{id}/ for FULL detail
          including features[], brands[], testimonials[].
    """
    permission_classes = [AllowAny]

    def get(self, request):
        def get_items(cat_name):
            try:
                cat = Category.objects.get(name__iexact=cat_name, is_active=True)
                qs  = cat.items.filter(is_active=True).order_by('order', 'name')
                return ItemListSerializer(qs, many=True, context={'request': request}).data
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


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY VIEWSET
# ─────────────────────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Portfolio Category CRUD

    Public:
        GET  /api/portfolio/categories/              list all active categories
        GET  /api/portfolio/categories/{name}/       detail + all items (lightweight)

    Admin (JWT required):
        POST   /api/portfolio/categories/            create
        PUT    /api/portfolio/categories/{name}/     full update
        PATCH  /api/portfolio/categories/{name}/     partial update
        DELETE /api/portfolio/categories/{name}/     delete + all its items
        POST   /api/portfolio/categories/{name}/toggle-active/

    Filters:
        ?is_active=true|false
        ?search=trading
        ?ordering=order|-order|name|-name
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# ITEM VIEWSET
# ─────────────────────────────────────────────────────────────────────────────

class ItemViewSet(viewsets.ModelViewSet):
    """
    Portfolio Item CRUD — all 5 form sections supported.

    ── PUBLIC endpoints ──────────────────────────────────────────────────────

    List (lightweight — no JSON arrays):
        GET /api/portfolio/items/
        GET /api/portfolio/items/?category__name=Trading
        GET /api/portfolio/items/?category__name=Distribution
        GET /api/portfolio/items/?category__name=Services
        GET /api/portfolio/items/?is_featured=true
        GET /api/portfolio/items/?search=cement
        GET /api/portfolio/items/?ordering=order
        GET /api/portfolio/items/?ordering=-created_at

    Full detail (includes features[], brands[], testimonials[]):
        GET /api/portfolio/items/{id}/

    ── ADMIN endpoints (JWT Bearer required) ─────────────────────────────────

        POST   /api/portfolio/items/           create
        PUT    /api/portfolio/items/{id}/      full update
        PATCH  /api/portfolio/items/{id}/      partial update
        DELETE /api/portfolio/items/{id}/      delete
        POST   /api/portfolio/items/{id}/toggle-featured/
        POST   /api/portfolio/items/{id}/toggle-active/

    ── FULL DETAIL RESPONSE (GET /api/portfolio/items/{id}/) ─────────────────

    {
        "success": true,
        "data": {
            "id": 1,
            "name": "CEMENT",
            "description": "...",
            "tags": "cement, OPC, PPC",
            "category": 1,
            "category_name": "Trading",
            "category_slug": "trading",
            "image": null,
            "image_url": null,
            "is_featured": true,
            "is_active": true,
            "order": 1,

            "hero_title": "Products Power Progress Explore Our Offer.",
            "banner_image": "/media/portfolio/banners/cement-banner.jpg",
            "banner_image_url": "https://kavalakat-api.onrender.com/media/portfolio/banners/cement-banner.jpg",

            "about_title": "Kavalakat Reliable Cement Supplier in Kerala",
            "about_description": "We handle 11,000–13,000 MT of cement...",
            "about_image": "/media/portfolio/about/cement-about.jpg",
            "about_image_url": "https://kavalakat-api.onrender.com/media/portfolio/about/cement-about.jpg",

            "features_title": "Cement Products",
            "features_image": "/media/portfolio/features/cement-faq.png",
            "features_image_url": "https://kavalakat-api.onrender.com/media/portfolio/features/cement-faq.png",
            "features_json": "[{\"title\":\"Top-Rated Dealer\",\"description\":\"...\"}]",
            "features": [
                {"title": "Top-Rated Dealer", "description": "Recognized as a leading dealer..."},
                {"title": "Customer-Focused Communication", "description": "..."},
                {"title": "Trust & Commitment in Service", "description": "..."},
                {"title": "Best Quality Products", "description": "..."}
            ],

            "brands_heading": "Trusted Cement Brands We Supply",
            "brands_json": "[{\"title\":\"ULTRATECH\",\"description\":\"...\",\"logo_url\":\"...\"}]",
            "brands": [
                {"title": "ULTRATECH", "description": "The company has a consolidated capacity...", "logo_url": "https://..."},
                {"title": "ACC", "description": "...", "logo_url": "https://..."},
                {"title": "JSW", "description": "...", "logo_url": "https://..."}
            ],

            "testimonials_json": "[{\"title\":\"...\",\"description\":\"...\",\"client_name\":\"...\"}]",
            "testimonials": [
                {"title": "OUTSTANDING MATERIAL QUALITY!", "description": "Delivery updates were timely...", "client_name": "Steve Mathew, Founder Egenslab"}
            ],

            "created_at": "2026-04-27T09:30:00+05:30",
            "updated_at": "2026-05-10T14:22:00+05:30"
        }
    }

    ── SENDING DATA (multipart/form-data) ────────────────────────────────────

        name               = "CEMENT"
        category           = 1
        tags               = "cement, OPC, PPC, Kerala"
        is_featured        = true
        is_active          = true
        order              = 1

        hero_title         = "Products Power Progress Explore Our Offer."
        banner_image       = <file upload>

        about_title        = "Kavalakat Reliable Cement Supplier in Kerala"
        about_description  = "We handle 11,000–13,000 MT of cement..."
        about_image        = <file upload>

        features_title     = "Cement Products"
        features_image     = <file upload>
        features_json      = '[{"title":"Top-Rated Dealer","description":"Recognized as a leading dealer..."}]'

        brands_heading     = "Trusted Cement Brands We Supply"
        brands_json        = '[{"title":"ULTRATECH","description":"...","logo_url":""}]'

        testimonials_json  = '[{"title":"Great!","description":"...","client_name":"John, Builder"}]'
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'category__name', 'category__slug',
                          'is_featured', 'is_active']
    search_fields      = ['name', 'description', 'tags', 'category__name',
                          'hero_title', 'about_title', 'about_description', 'brands_heading']
    ordering_fields    = ['order', 'created_at', 'name', 'category__order']

    def get_serializer_class(self):
        """
        list action   → ItemListSerializer (lightweight, fast, no JSON arrays)
        all others    → ItemSerializer     (full, with features/brands/testimonials)
        """
        if self.action == 'list':
            return ItemListSerializer
        return ItemSerializer

    def get_queryset(self):
        qs = Item.objects.select_related('category').all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True, category__is_active=True)
        return qs

    # ── List ──────────────────────────────────────────────────────────────────
    def list(self, request, *args, **kwargs):
        """
        Returns lightweight list — no features/brands/testimonials.
        Use GET /api/portfolio/items/{id}/ for the full 5-section detail.
        """
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

    # ── Retrieve ──────────────────────────────────────────────────────────────
    def retrieve(self, request, *args, **kwargs):
        """
        Returns FULL item detail including all 5 sections:
        Section 1: hero_title + banner_image_url
        Section 2: about_title + about_description + about_image_url
        Section 3: features_title + features_image_url + features[] array
        Section 4: brands_heading + brands[] array with logo_url
        Section 5: testimonials[] array
        """
        obj = self.get_object()
        return Response({
            'success': True,
            'data':    ItemSerializer(obj, context={'request': request}).data,
        })

    # ── Create ────────────────────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        """
        POST /api/portfolio/items/
        Content-Type: multipart/form-data  (supports image uploads)
        Authorization: Bearer <token>

        Pass features_json, brands_json, testimonials_json as JSON strings.
        """
        s = ItemSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({
            'success': True,
            'message': f'Item "{obj.name}" created.',
            'data':    ItemSerializer(obj, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, request, *args, **kwargs):
        """
        PUT   /api/portfolio/items/{id}/   full update
        PATCH /api/portfolio/items/{id}/   partial update
        Content-Type: multipart/form-data  (supports image uploads)
        Authorization: Bearer <token>
        """
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

    # ── Destroy ───────────────────────────────────────────────────────────────
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        n   = obj.name
        obj.delete()
        return Response({
            'success': True,
            'message': f'Item "{n}" deleted.',
        }, status=status.HTTP_200_OK)

    # ── Toggle featured ───────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-featured')
    def toggle_featured(self, request, pk=None):
        """
        POST /api/portfolio/items/{id}/toggle-featured/
        Authorization: Bearer <token>
        Response: { "success": true, "is_featured": true, "message": "Item featured." }
        """
        obj = self.get_object()
        obj.is_featured = not obj.is_featured
        obj.save(update_fields=['is_featured'])
        return Response({
            'success':     True,
            'message':     f'Item {"featured" if obj.is_featured else "unfeatured"}.',
            'is_featured': obj.is_featured,
        })

    # ── Toggle active ─────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """
        POST /api/portfolio/items/{id}/toggle-active/
        Authorization: Bearer <token>
        Response: { "success": true, "is_active": false, "message": "Item deactivated." }
        """
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({
            'success':   True,
            'message':   f'Item {"activated" if obj.is_active else "deactivated"}.',
            'is_active': obj.is_active,
        })