from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
User = get_user_model()

class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order','name']
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name

class Post(models.Model):
    STATUS_DRAFT     = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED  = 'archived'
    STATUS_CHOICES   = [(STATUS_DRAFT,'Draft'),(STATUS_PUBLISHED,'Published'),(STATUS_ARCHIVED,'Archived')]
    title            = models.CharField(max_length=255)
    slug             = models.SlugField(unique=True, max_length=255, blank=True)
    content          = models.TextField()
    excerpt          = models.TextField(blank=True)
    image            = models.ImageField(upload_to='blog/posts/', blank=True, null=True)
    category         = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    tags             = models.CharField(max_length=255, blank=True)
    is_ai_generated  = models.BooleanField(default=False)
    is_featured      = models.BooleanField(default=False)
    views            = models.PositiveIntegerField(default=0)
    meta_title       = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    published_at     = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self): return self.title
    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views=models.F('views')+1)
