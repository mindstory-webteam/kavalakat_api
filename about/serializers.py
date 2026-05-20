from rest_framework import serializers
from .models import About, Strength, Milestone, Project, Gallery, TeamMember


# ── Helper ────────────────────────────────────────────────────────────────────
def build_image_url(obj_field, context):
    """
    Return an absolute URL when a request object is available in the serializer
    context, otherwise fall back to the relative /media/... path so that
    image_url is never silently None just because the context is missing.
    """
    if not obj_field:
        return None
    req = context.get('request')
    if req:
        return req.build_absolute_uri(obj_field.url)
    return obj_field.url          # relative URL – still usable by the frontend


# ── Serializers ───────────────────────────────────────────────────────────────

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model            = About
        fields           = [
            'id', 'title', 'description', 'vision', 'mission',
            'founded_year', 'employee_count', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class StrengthSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Strength
        fields = ['id', 'title', 'description', 'icon', 'image', 'image_url', 'order', 'is_active']

    def get_image_url(self, obj):
        return build_image_url(obj.image, self.context)


class MilestoneSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model            = Milestone
        fields           = [
            'id', 'year', 'title', 'description',
            'image', 'image_url', 'tags', 'tags_list', 'order',
        ]
        read_only_fields = ['id']

    def get_image_url(self, obj):
        return build_image_url(obj.image, self.context)

    def get_tags_list(self, obj):
        return obj.tags_list()


class ProjectSerializer(serializers.ModelSerializer):
    image_url       = serializers.SerializerMethodField()
    client_logo_url = serializers.SerializerMethodField()

    class Meta:
        model            = Project
        fields           = [
            'id', 'title', 'description',
            'client', 'client_logo', 'client_logo_url', 'client_location',
            'location', 'year', 'tag',
            'image', 'image_url',
            'contact_url', 'is_featured', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        return build_image_url(obj.image, self.context)

    def get_client_logo_url(self, obj):
        return build_image_url(obj.client_logo, self.context)


class GallerySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model            = Gallery
        fields           = ['id', 'title', 'image', 'image_url', 'caption', 'order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        return build_image_url(obj.image, self.context)


class TeamMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model            = TeamMember
        fields           = [
            'id', 'name', 'role', 'image', 'image_url',
            'social_platform', 'social_url', 'order', 'is_active',
        ]
        read_only_fields = ['id']

    def get_image_url(self, obj):
        return build_image_url(obj.image, self.context)