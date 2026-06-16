from rest_framework import serializers
from django.utils import timezone

from kavalakat.validators import (
    validate_image_extension, validate_image_content_type, validate_image_size,
)
from .models import Event, EventCategory, EventImage


def _abs_url(field, request):
    if not field:
        return None
    try:
        url = field.url
    except Exception:
        return None
    return request.build_absolute_uri(url) if request else url


def _check_image(value):
    if not value:
        return value
    validate_image_extension(value)
    validate_image_content_type(value)
    validate_image_size(value)
    return value


# ── Event Category ────────────────────────────────────────────────────────────
class EventCategorySerializer(serializers.ModelSerializer):
    event_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = EventCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'status',
            'event_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'event_count', 'created_at', 'updated_at']

    def get_event_count(self, obj):
        return getattr(obj, 'event_count_annotated', None) or obj.events.count()

    def validate_name(self, v):
        v = v.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Category name must be at least 2 characters.')
        return v


# ── Gallery image ─────────────────────────────────────────────────────────────
class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = EventImage
        fields = ['id', 'image', 'image_url', 'caption', 'order', 'uploaded_at']
        read_only_fields = ['id', 'image_url', 'uploaded_at']
        extra_kwargs = {'image': {'required': True}}

    def get_image_url(self, obj):
        return _abs_url(obj.image, self.context.get('request'))

    def validate_image(self, v):
        return _check_image(v)


# ── Event list (lighter — no nested gallery detail) ────────────────────────────
class EventListSerializer(serializers.ModelSerializer):
    category_name      = serializers.CharField(source='category.name',
                                               read_only=True, default=None)
    featured_image_url = serializers.SerializerMethodField(read_only=True)
    organizer_logo_url = serializers.SerializerMethodField(read_only=True)
    images             = serializers.SerializerMethodField(read_only=True)
    is_upcoming        = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'event_name', 'slug',
            'short_description', 'is_featured',
            'organizer', 'organizer_logo_url',
            'featured_image_url', 'images',
            'category', 'category_name', 'tag',
            'event_date', 'event_time', 'venue', 'location', 'is_upcoming',
            'registration_url', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_featured_image_url(self, obj):
        return _abs_url(obj.featured_image, self.context.get('request'))

    def get_organizer_logo_url(self, obj):
        return _abs_url(obj.organizer_logo, self.context.get('request'))

    def get_images(self, obj):
        req  = self.context.get('request')
        urls = []
        fi   = _abs_url(obj.featured_image, req)
        if fi:
            urls.append(fi)
        for gi in obj.gallery_images.all():
            u = _abs_url(gi.image, req)
            if u:
                urls.append(u)
        return urls


# ── Event detail (full) ────────────────────────────────────────────────────────
class EventSerializer(serializers.ModelSerializer):
    category_name      = serializers.CharField(source='category.name',
                                               read_only=True, default=None)
    featured_image_url = serializers.SerializerMethodField(read_only=True)
    organizer_logo_url = serializers.SerializerMethodField(read_only=True)
    gallery_images     = EventImageSerializer(many=True, read_only=True)
    images             = serializers.SerializerMethodField(read_only=True)
    is_upcoming        = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Event
        fields = [
            'id', 'event_name', 'slug',
            'short_description', 'description', 'is_featured',
            'organizer', 'organizer_logo', 'organizer_logo_url',
            'featured_image', 'featured_image_url',
            'gallery_images', 'images',
            'category', 'category_name', 'tag',
            'event_date', 'event_time', 'venue', 'location', 'is_upcoming',
            'registration_url', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'category_name',
            'featured_image_url', 'organizer_logo_url',
            'gallery_images', 'images',
            'is_upcoming', 'created_at', 'updated_at',
        ]
        extra_kwargs = {
            'featured_image':    {'required': False, 'allow_null': True},
            'organizer_logo':    {'required': False, 'allow_null': True},
            'registration_url':  {'required': False, 'allow_blank': True},
            'short_description': {'required': False, 'allow_blank': True},
        }

    def get_featured_image_url(self, obj):
        return _abs_url(obj.featured_image, self.context.get('request'))

    def get_organizer_logo_url(self, obj):
        return _abs_url(obj.organizer_logo, self.context.get('request'))

    def get_images(self, obj):
        req  = self.context.get('request')
        urls = []
        fi   = _abs_url(obj.featured_image, req)
        if fi:
            urls.append(fi)
        for gi in obj.gallery_images.all():
            u = _abs_url(gi.image, req)
            if u:
                urls.append(u)
        return urls

    def validate_featured_image(self, v):  return _check_image(v)
    def validate_organizer_logo(self, v):  return _check_image(v)

    def validate_event_name(self, v):
        v = v.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Event name must be at least 2 characters.')
        return v
