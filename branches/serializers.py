from rest_framework import serializers

from kavalakat.validators import (
    validate_image_content_type,
    validate_image_extension,
    validate_image_size,
)
from .models import BranchLocation


class BranchLocationSerializer(serializers.ModelSerializer):
    location_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BranchLocation
        fields = [
            'id', 'branch_name', 'address', 'phone_number', 'email',
            'google_map_link', 'location_image', 'location_image_url',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'location_image_url', 'created_at', 'updated_at']
        extra_kwargs = {
            'location_image': {'required': False, 'allow_null': True},
        }

    def get_location_image_url(self, obj):
        if not obj.location_image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.location_image.url) if request else obj.location_image.url

    def validate_branch_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Branch name must be at least 2 characters.')
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate_location_image(self, value):
        if value in (None, ''):
            return value
        validate_image_extension(value)
        validate_image_content_type(value)
        validate_image_size(value)
        return value
