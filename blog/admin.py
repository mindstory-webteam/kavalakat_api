from django.contrib import admin
from django.utils import timezone
from .models import Category, Post

@admin.register(Category)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug','order']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['slug']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ['title','category','author','status','is_featured','views','created_at']
    list_filter   = ['status','category','is_featured','is_ai_generated']
    search_fields = ['title','content','tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug','views','created_at','updated_at']
    date_hierarchy = 'created_at'
    actions = ['publish_posts','unpublish_posts']
    def publish_posts(self, request, qs):
        qs.update(status=Post.STATUS_PUBLISHED, published_at=timezone.now())
    publish_posts.short_description = 'Publish selected'
    def unpublish_posts(self, request, qs):
        qs.update(status=Post.STATUS_DRAFT)
    unpublish_posts.short_description = 'Move to draft'
