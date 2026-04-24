from rest_framework import serializers
from .models import AIGenerationLog

class GenerateBlogInputSerializer(serializers.Serializer):
    topic         = serializers.CharField(max_length=500)
    save_as_draft = serializers.BooleanField(default=False)
    category_id   = serializers.IntegerField(required=False, allow_null=True)
    author_id     = serializers.IntegerField(required=False, allow_null=True)
    def validate_topic(self, v):
        v=v.strip()
        if len(v)<3: raise serializers.ValidationError('Topic must be at least 3 characters.')
        return v

class AIGenerationLogSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField()
    blog_post_slug    = serializers.CharField(source='blog_post.slug', read_only=True, default=None)
    class Meta:
        model=AIGenerationLog
        fields=['id','topic','generated_title','generated_excerpt','model_used','tokens_used',
                'status','error_message','requested_by','requested_by_name','saved_as_post',
                'blog_post','blog_post_slug','created_at']
        read_only_fields=fields
    def get_requested_by_name(self, obj):
        return (obj.requested_by.get_full_name() or obj.requested_by.username) if obj.requested_by else 'Anonymous'
