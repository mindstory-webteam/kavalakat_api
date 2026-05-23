from rest_framework import serializers
from .models import (
    ServiceCategory, Service, ServiceAbout, ServiceCounter, ServiceOffer,
    ServiceFeatureSection, ServiceFeature,
    ServiceHighlight, ServiceLocation, ServiceNearbyPlace,
)


def build_image_url(obj_field, context):
    if not obj_field:
        return None
    req = context.get('request')
    if req:
        return req.build_absolute_uri(obj_field.url)
    return obj_field.url


class ServiceAboutSerializer(serializers.ModelSerializer):
    left_side_image_url = serializers.SerializerMethodField()
    gallery_image_1_url = serializers.SerializerMethodField()
    gallery_image_2_url = serializers.SerializerMethodField()
    gallery_image_3_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceAbout
        fields = [
            'id', 'service', 'main_title', 'sub_title', 'description',
            'left_side_image', 'left_side_image_url',
            'gallery_image_1', 'gallery_image_1_url',
            'gallery_image_2', 'gallery_image_2_url',
            'gallery_image_3', 'gallery_image_3_url',
            'button_text', 'button_link', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_left_side_image_url(self, obj): return build_image_url(obj.left_side_image, self.context)
    def get_gallery_image_1_url(self, obj): return build_image_url(obj.gallery_image_1, self.context)
    def get_gallery_image_2_url(self, obj): return build_image_url(obj.gallery_image_2, self.context)
    def get_gallery_image_3_url(self, obj): return build_image_url(obj.gallery_image_3, self.context)


class ServiceCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCounter
        fields = ['id', 'service', 'counter_title', 'counter_number', 'short_description', 'icon', 'order', 'is_active']
        read_only_fields = ['id']


class ServiceOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOffer
        fields = ['id', 'service', 'offer_title', 'offer_icon', 'short_description', 'order', 'is_active']
        read_only_fields = ['id']


class ServiceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFeature
        fields = ['id', 'section', 'feature_title', 'feature_description', 'order']
        read_only_fields = ['id']


class ServiceFeatureSectionSerializer(serializers.ModelSerializer):
    left_main_image_url = serializers.SerializerMethodField()
    features = ServiceFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceFeatureSection
        fields = ['id', 'service', 'section_title', 'left_main_image', 'left_main_image_url', 'main_description', 'features', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_left_main_image_url(self, obj): return build_image_url(obj.left_main_image, self.context)


class ServiceHighlightSerializer(serializers.ModelSerializer):
    highlight_video_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceHighlight
        fields = ['id', 'service', 'section_title', 'section_sub_title', 'highlight_title', 'highlight_description', 'highlight_video', 'highlight_video_url', 'display_order', 'is_active']
        read_only_fields = ['id']

    def get_highlight_video_url(self, obj): return build_image_url(obj.highlight_video, self.context)


class ServiceNearbyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceNearbyPlace
        fields = ['id', 'location', 'nearby_place_name', 'distance', 'map_link', 'order']
        read_only_fields = ['id']


class ServiceLocationSerializer(serializers.ModelSerializer):
    left_main_image_url = serializers.SerializerMethodField()
    nearby_places = ServiceNearbyPlaceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceLocation
        fields = ['id', 'service', 'location_main_title', 'location_main_sub_title', 'location_main_description', 'left_main_image', 'left_main_image_url', 'nearby_places', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_left_main_image_url(self, obj): return build_image_url(obj.left_main_image, self.context)


class ServiceCategorySerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'order', 'is_active', 'service_count']
        read_only_fields = ['id', 'slug']

    def get_service_count(self, obj):
        return obj.services.count()


class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    about = ServiceAboutSerializer(read_only=True)
    feature_section = ServiceFeatureSectionSerializer(read_only=True)
    location = ServiceLocationSerializer(read_only=True)
    counters = ServiceCounterSerializer(many=True, read_only=True)
    offers = ServiceOfferSerializer(many=True, read_only=True)
    highlights = ServiceHighlightSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'slug', 'description', 'icon', 'image', 'image_url', 'is_active', 'is_featured', 'order', 'created_at', 'about', 'counters', 'offers', 'feature_section', 'highlights', 'location']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj): return build_image_url(obj.image, self.context)
