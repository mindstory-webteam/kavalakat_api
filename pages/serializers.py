from rest_framework import serializers
from .models import Page

class PageSerializer(serializers.ModelSerializer):
    banner_image_url = serializers.SerializerMethodField()
    class Meta:
        model  = Page
        fields = ['id','title','slug','content','banner_image','banner_image_url',
                  'meta_title','meta_description','is_active','order','created_at','updated_at']
        read_only_fields = ['id','slug','created_at','updated_at']
    def get_banner_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.banner_image.url) if obj.banner_image and req else None
    def validate_title(self, v):
        if len(v.strip()) < 2: raise serializers.ValidationError('Title too short.')
        return v.strip()
