from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    title            = models.CharField(max_length=255)
    slug             = models.SlugField(unique=True, max_length=255, blank=True)
    content          = models.TextField(blank=True)
    banner_image     = models.ImageField(upload_to='pages/banners/', blank=True, null=True)
    meta_title       = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    is_active        = models.BooleanField(default=True)
    order            = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
