from rest_framework import serializers
from .models import Category, Item


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    image_url     = serializers.SerializerMethodField()

    class Meta:
        model  = Item
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'image_url',
            'tags', 'category', 'category_name', 'category_slug',
            'is_featured', 'is_active', 'order', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.image.url) if obj.image and req else None

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip().upper()


class CategorySerializer(serializers.ModelSerializer):
    """Full serializer — includes nested items list."""
    items      = ItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'order', 'is_active', 'item_count', 'items', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category name must be at least 2 characters.')
        return value.strip()


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight — no nested items. Used for list views."""
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'order', 'is_active', 'item_count',
        ]
        read_only_fields = ['id', 'slug']


class PortfolioPageSerializer(serializers.Serializer):
    """
    Returns the entire portfolio page in one response:
    { trading: [...], distribution: [...], services: [...] }
    Matches the 3-column layout on the Kavalakat website.
    """
    trading      = ItemSerializer(many=True)
    distribution = ItemSerializer(many=True)
    services     = ItemSerializer(many=True)
