from rest_framework import serializers
from .models import Category, Post

class BlogCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    class Meta:
        model  = Category
        fields = ['id','name','slug','description','order','post_count']
        read_only_fields = ['id','slug']
    def get_post_count(self, obj):
        return obj.posts.filter(status=Post.STATUS_PUBLISHED).count()

class PostListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    author_name   = serializers.SerializerMethodField()
    image_url     = serializers.SerializerMethodField()
    class Meta:
        model  = Post
        fields = ['id','title','slug','excerpt','image','image_url','category','category_name',
                  'category_slug','author','author_name','status','tags','is_featured',
                  'is_ai_generated','views','created_at','published_at']
        read_only_fields = ['id','slug','views','created_at','updated_at']
    def get_author_name(self, obj):
        return (obj.author.get_full_name() or obj.author.username) if obj.author else None
    def get_image_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.image.url) if obj.image and req else None

class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content','meta_title','meta_description','updated_at']

class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Post
        fields = ['title','content','excerpt','image','category','author','status','tags',
                  'is_featured','meta_title','meta_description','published_at']
    def validate_title(self, v):
        if len(v.strip()) < 5: raise serializers.ValidationError('Title must be at least 5 characters.')
        return v.strip()
