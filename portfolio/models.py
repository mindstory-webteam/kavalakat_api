"""
portfolio/models.py  (FIXED)
─────────────────────────────
FIX: Removed hardcoded choices=[...] from Category.name.
     The old code locked the name field to only 3 values:
     Trading / Distribution / Services.
     Any other category (e.g. "NEW TEST") could not be saved properly.

     Now name is a free CharField — any category name works.
     No data is lost; existing rows are untouched.

     Run after replacing this file:
         python manage.py makemigrations portfolio
         python manage.py migrate
"""
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    # ── FIXED: removed choices=[...] ─────────────────────────────────────────
    # Old:  name = models.CharField(max_length=100, choices=CHOICES, unique=True)
    # New:  name is free-text — any category you create in the CMS is valid.
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering            = ['order', 'name']
        verbose_name        = 'Portfolio Category'
        verbose_name_plural = 'Portfolio Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Item(models.Model):
    # ── Basics ────────────────────────────────────────────────────────────────
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags        = models.CharField(max_length=500, blank=True)
    category    = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='items'
    )
    image       = models.ImageField(upload_to='portfolio/items/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    # ── Section 1 – Hero ──────────────────────────────────────────────────────
    hero_title   = models.CharField(max_length=300, blank=True)
    banner_image = models.ImageField(upload_to='portfolio/banners/', blank=True, null=True)

    # ── Section 2 – About ─────────────────────────────────────────────────────
    about_title       = models.CharField(max_length=300, blank=True)
    about_description = models.TextField(blank=True)
    about_image       = models.ImageField(upload_to='portfolio/about/', blank=True, null=True)

    # ── Section 3 – Features ──────────────────────────────────────────────────
    features_title = models.CharField(max_length=300, blank=True)
    features_image = models.ImageField(upload_to='portfolio/features/', blank=True, null=True)
    features_json  = models.TextField(blank=True, default='[]')

    # ── Section 4 – Brands ────────────────────────────────────────────────────
    brands_heading = models.CharField(max_length=300, blank=True)
    brands_json    = models.TextField(blank=True, default='[]')

    # ── Section 5 – Testimonials ──────────────────────────────────────────────
    testimonials_json = models.TextField(blank=True, default='[]')

    # ── Meta ──────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.category.name})'
