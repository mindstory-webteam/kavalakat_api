from rest_framework import serializers
from .models import About, Strength, Milestone, Project, Gallery

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model  = About
        fields = ['id','title','description','vision','mission','founded_year','employee_count','updated_at']
        read_only_fields = ['id','updated_at']

class StrengthSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Strength
        fields = ['id','title','description','icon','order','is_active']

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Milestone
        fields = ['id','year','title','description','order']

class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model  = Project
        fields = ['id','title','description','client','location','year','image','image_url','is_featured','created_at']
        read_only_fields = ['id','created_at']
    def get_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.image.url) if obj.image and req else None

class GallerySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model  = Gallery
        fields = ['id','title','image','image_url','caption','order','is_active','created_at']
        read_only_fields = ['id','created_at']
    def get_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.image.url) if obj.image and req else None
