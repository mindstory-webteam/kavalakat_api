import json
from rest_framework import serializers
from .models import Category, Item


class ItemSerializer(serializers.ModelSerializer):
    category_name      = serializers.CharField(source='category.name', read_only=True)
    category_slug      = serializers.CharField(source='category.slug', read_only=True)
    image_url          = serializers.SerializerMethodField()
    banner_image_url   = serializers.SerializerMethodField()
    about_image_url    = serializers.SerializerMethodField()
    features_image_url = serializers.SerializerMethodField()
    features           = serializers.SerializerMethodField()
    brands             = serializers.SerializerMethodField()
    testimonials       = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            'id', 'name', 'description', 'image', 'image_url', 'tags',
            'category', 'category_name', 'category_slug',
            'is_featured', 'is_active', 'order',
            'hero_title', 'banner_image', 'banner_image_url',
            'about_title', 'about_description', 'about_image', 'about_image_url',
            'features_title', 'features_image', 'features_image_url',
            'features_json', 'features',
            'brands_heading', 'brands_json', 'brands',
            'testimonials_json', 'testimonials',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'category_name', 'category_slug',
            'image_url', 'banner_image_url', 'about_image_url', 'features_image_url',
            'features', 'brands', 'testimonials',
        ]

    def _get_abs_url(self, file_field):
        if not file_field:
            return None
        req = self.context.get('request')
        return req.build_absolute_uri(file_field.url) if req else file_field.url

    def get_image_url(self, obj):          return self._get_abs_url(obj.image)
    def get_banner_image_url(self, obj):   return self._get_abs_url(obj.banner_image)
    def get_about_image_url(self, obj):    return self._get_abs_url(obj.about_image)
    def get_features_image_url(self, obj): return self._get_abs_url(obj.features_image)
    def get_features(self, obj):           return obj.get_features()
    def get_testimonials(self, obj):       return obj.get_testimonials()

    def get_brands(self, obj):
        brands = obj.get_brands()
        req = self.context.get('request')
        if req:
            for brand in brands:
                logo = brand.get('logo_url', '')
                if logo and logo.startswith('/'):
                    brand['logo_url'] = req.build_absolute_uri(logo)
        return brands

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip().upper()

    def _validate_json_list(self, value, field_name):
        if not value:
            return '[]'
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise serializers.ValidationError(
                    f'{field_name} must be a JSON array.'
                )
            return value
        except json.JSONDecodeError:
            raise serializers.ValidationError(f'{field_name} must be valid JSON.')

    def validate_features_json(self, value):     return self._validate_json_list(value, 'features_json')
    def validate_brands_json(self, value):       return self._validate_json_list(value, 'brands_json')
    def validate_testimonials_json(self, value): return self._validate_json_list(value, 'testimonials_json')


# ── FIXED: ItemListSerializer now includes ALL fields ──────────────────────────
class ItemListSerializer(serializers.ModelSerializer):
    """
    Used for list views AND /api/portfolio/page/.
    NOW includes: about_description, features, brands, testimonials
    so the frontend gets everything in one call.
    """
    category_name      = serializers.CharField(source='category.name', read_only=True)
    category_slug      = serializers.CharField(source='category.slug', read_only=True)
    image_url          = serializers.SerializerMethodField()
    banner_image_url   = serializers.SerializerMethodField()
    about_image_url    = serializers.SerializerMethodField()
    features_image_url = serializers.SerializerMethodField()
    features           = serializers.SerializerMethodField()
    brands             = serializers.SerializerMethodField()
    testimonials       = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            'id', 'name', 'description', 'image', 'image_url', 'tags',
            'category', 'category_name', 'category_slug',
            # Section 1 — Hero
            'hero_title', 'banner_image', 'banner_image_url',
            # Section 2 — About  ← FIXED: about_description now included
            'about_title', 'about_description', 'about_image', 'about_image_url',
            # Section 3 — Features  ← FIXED: features array now included
            'features_title', 'features_image', 'features_image_url', 'features',
            # Section 4 — Brands  ← FIXED: brands array now included
            'brands_heading', 'brands',
            # Section 5 — Testimonials  ← FIXED: testimonials array now included
            'testimonials',
            'is_featured', 'is_active', 'order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _get_abs_url(self, file_field):
        if not file_field:
            return None
        req = self.context.get('request')
        return req.build_absolute_uri(file_field.url) if req else file_field.url

    def get_image_url(self, obj):          return self._get_abs_url(obj.image)
    def get_banner_image_url(self, obj):   return self._get_abs_url(obj.banner_image)
    def get_about_image_url(self, obj):    return self._get_abs_url(obj.about_image)
    def get_features_image_url(self, obj): return self._get_abs_url(obj.features_image)
    def get_features(self, obj):           return obj.get_features()
    def get_testimonials(self, obj):       return obj.get_testimonials()

    def get_brands(self, obj):
        brands = obj.get_brands()
        req = self.context.get('request')
        if req:
            for brand in brands:
                logo = brand.get('logo_url', '')
                if logo and logo.startswith('/'):
                    brand['logo_url'] = req.build_absolute_uri(logo)
        return brands


class CategorySerializer(serializers.ModelSerializer):
    items      = ItemListSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order',
                  'is_active', 'item_count', 'items']
        read_only_fields = ['id', 'slug']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category name must be at least 2 characters.')
        return value.strip()


class CategoryListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order',
                  'is_active', 'item_count']
        read_only_fields = ['id', 'slug']


class PortfolioPageSerializer(serializers.Serializer):
    trading      = ItemListSerializer(many=True)
    distribution = ItemListSerializer(many=True)
    services     = ItemListSerializer(many=True)