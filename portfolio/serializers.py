import json
from rest_framework import serializers
from .models import Category, Item


# ─────────────────────────────────────────────────────────────────────────────
# ITEM SERIALIZER — full detail with all 5 section fields
# ─────────────────────────────────────────────────────────────────────────────

class ItemSerializer(serializers.ModelSerializer):
    # Category info (read-only)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    # Image URLs (absolute URLs)
    image_url          = serializers.SerializerMethodField()
    banner_image_url   = serializers.SerializerMethodField()
    about_image_url    = serializers.SerializerMethodField()
    features_image_url = serializers.SerializerMethodField()

    # Parsed JSON arrays — returned as proper arrays (read-only)
    features     = serializers.SerializerMethodField()
    brands       = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            # ── Basic ───────────────────────────────────────────────────────
            'id',
            'name',
            'description',
            'image',
            'image_url',
            'tags',
            'category',
            'category_name',
            'category_slug',
            'is_featured',
            'is_active',
            'order',

            # ── Section 1: Hero Banner ───────────────────────────────────────
            'hero_title',
            'banner_image',
            'banner_image_url',

            # ── Section 2: About ─────────────────────────────────────────────
            'about_title',
            'about_description',
            'about_image',
            'about_image_url',

            # ── Section 3: Features ──────────────────────────────────────────
            'features_title',
            'features_image',
            'features_image_url',
            'features_json',   # writable raw JSON
            'features',        # parsed array (read-only)

            # ── Section 4: Brands ────────────────────────────────────────────
            'brands_heading',
            'brands_json',     # writable raw JSON
            'brands',          # parsed array (read-only)

            # ── Section 5: Testimonials ──────────────────────────────────────
            'testimonials_json',  # writable raw JSON
            'testimonials',       # parsed array (read-only)

            # ── Timestamps ───────────────────────────────────────────────────
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'category_name',
            'category_slug',
            'image_url',
            'banner_image_url',
            'about_image_url',
            'features_image_url',
            'features',
            'brands',
            'testimonials',
        ]

    # ── Image URL helpers ──────────────────────────────────────────────────────
    def _get_abs_url(self, file_field):
        """Return absolute URL for any ImageField."""
        if not file_field:
            return None
        req = self.context.get('request')
        return req.build_absolute_uri(file_field.url) if req else file_field.url

    def get_image_url(self, obj):
        return self._get_abs_url(obj.image)

    def get_banner_image_url(self, obj):
        return self._get_abs_url(obj.banner_image)

    def get_about_image_url(self, obj):
        return self._get_abs_url(obj.about_image)

    def get_features_image_url(self, obj):
        return self._get_abs_url(obj.features_image)

    # ── JSON array helpers ─────────────────────────────────────────────────────
    def get_features(self, obj):
        """Returns features as a parsed list of dicts."""
        return obj.get_features()

    def get_brands(self, obj):
        """Returns brands as a parsed list of dicts with absolute logo URLs."""
        brands = obj.get_brands()
        req = self.context.get('request')
        if req:
            for brand in brands:
                logo = brand.get('logo_url', '')
                if logo and logo.startswith('/'):
                    brand['logo_url'] = req.build_absolute_uri(logo)
        return brands

    def get_testimonials(self, obj):
        """Returns testimonials as a parsed list of dicts."""
        return obj.get_testimonials()

    # ── Validation ─────────────────────────────────────────────────────────────
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip().upper()

    def _validate_json_list(self, value, field_name):
        """Validate that a field is a valid JSON array."""
        if not value:
            return '[]'
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError(
                    f'{field_name} must be a JSON array, e.g. [{{"title": "...", "description": "..."}}]'
                )
            return value
        except json.JSONDecodeError:
            raise serializers.ValidationError(
                f'{field_name} must be valid JSON. Got: {value[:100]}'
            )

    def validate_features_json(self, value):
        return self._validate_json_list(value, 'features_json')

    def validate_brands_json(self, value):
        return self._validate_json_list(value, 'brands_json')

    def validate_testimonials_json(self, value):
        return self._validate_json_list(value, 'testimonials_json')


# ─────────────────────────────────────────────────────────────────────────────
# ITEM LIST SERIALIZER — lightweight for list views, no JSON arrays
# ─────────────────────────────────────────────────────────────────────────────

class ItemListSerializer(serializers.ModelSerializer):
    """
    Used for:
    - GET /api/portfolio/items/ (list)
    - Nested inside CategorySerializer
    - GET /api/portfolio/page/ (3-column layout)

    Does NOT include heavy JSON fields (features, brands, testimonials).
    Use ItemSerializer for full detail on a single item.
    """
    category_name    = serializers.CharField(source='category.name', read_only=True)
    category_slug    = serializers.CharField(source='category.slug', read_only=True)
    image_url        = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            'id',
            'name',
            'description',
            'image',
            'image_url',
            'tags',
            'category',
            'category_name',
            'category_slug',
            # Section 1 (title + URL only — no upload field)
            'hero_title',
            'banner_image',
            'banner_image_url',
            # Section 2 (title only)
            'about_title',
            # Section 3 (title only)
            'features_title',
            # Section 4 (heading only)
            'brands_heading',
            'is_featured',
            'is_active',
            'order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _get_abs_url(self, file_field):
        if not file_field:
            return None
        req = self.context.get('request')
        return req.build_absolute_uri(file_field.url) if req else file_field.url

    def get_image_url(self, obj):
        return self._get_abs_url(obj.image)

    def get_banner_image_url(self, obj):
        return self._get_abs_url(obj.banner_image)


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    """
    Full category detail — includes nested items (lightweight list version).
    Used for: GET /api/portfolio/categories/{name}/
    """
    items      = ItemListSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'icon',
            'order',
            'is_active',
            'item_count',
            'items',
        ]
        read_only_fields = ['id', 'slug']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category name must be at least 2 characters.')
        return value.strip()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight — no nested items.
    Used for: GET /api/portfolio/categories/
    """
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'icon',
            'order',
            'is_active',
            'item_count',
        ]
        read_only_fields = ['id', 'slug']


# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO PAGE SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────

class PortfolioPageSerializer(serializers.Serializer):
    """
    Used for GET /api/portfolio/page/
    Returns full 3-column layout:
    {
        "trading":      [...],
        "distribution": [...],
        "services":     [...]
    }
    """
    trading      = ItemListSerializer(many=True)
    distribution = ItemListSerializer(many=True)
    services     = ItemListSerializer(many=True)
