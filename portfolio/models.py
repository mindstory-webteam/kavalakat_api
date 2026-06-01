import json
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    # FIXED: removed hardcoded choices=[...] so any category name is valid
    # Old: name = models.CharField(max_length=100, choices=CHOICES, unique=True)
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
    # ── Core ──────────────────────────────────────────────────────────────────
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name        = models.CharField(max_length=255, help_text='Displayed UPPERCASE on website')
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='portfolio/items/', blank=True, null=True)
    tags        = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    # ── Section 1: Hero Banner ────────────────────────────────────────────────
    hero_title   = models.CharField(
        max_length=500, blank=True,
        help_text='Headline shown at top of product page banner'
    )
    banner_image = models.ImageField(
        upload_to='portfolio/banners/', blank=True, null=True,
        help_text='Full-width banner image — 1920x600px recommended'
    )

    # ── Section 2: About ──────────────────────────────────────────────────────
    about_title       = models.CharField(max_length=500, blank=True)
    about_description = models.TextField(blank=True)
    about_image       = models.ImageField(
        upload_to='portfolio/about/', blank=True, null=True
    )

    # ── Section 3: Features (accordion) ──────────────────────────────────────
    features_title = models.CharField(
        max_length=255, blank=True,
        help_text='e.g. Steel Products, Cement Products'
    )
    features_image = models.ImageField(
        upload_to='portfolio/features/', blank=True, null=True,
        help_text='Large image shown beside feature accordion'
    )
    features_json = models.TextField(
        blank=True, default='[]',
        help_text='JSON array: [{"title": "...", "description": "..."}, ...]'
    )

    # ── Section 4: Trusted Brands ─────────────────────────────────────────────
    brands_heading = models.CharField(
        max_length=255, blank=True,
        help_text='e.g. Trusted Steel Brands We Supply'
    )
    brands_json = models.TextField(
        blank=True, default='[]',
        help_text='JSON array: [{"title": "VIZAG", "description": "...", "logo_url": "..."}, ...]'
    )

    # ── Section 5: Testimonials ───────────────────────────────────────────────
    testimonials_json = models.TextField(
        blank=True, default='[]',
        help_text='JSON array: [{"title": "...", "description": "...", "client_name": "..."}, ...]'
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['order', 'name']
        verbose_name        = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def save(self, *args, **kwargs):
        self.name = self.name.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} [{self.category.name}]'

    # ── JSON helpers ──────────────────────────────────────────────────────────
    def _parse_json(self, field_value):
        try:
            data = json.loads(field_value) if field_value else []
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def get_features(self):
        """Returns features as a list of dicts: [{"title": "...", "description": "..."}, ...]"""
        return self._parse_json(self.features_json)

    def get_brands(self):
        """Returns brands as a list of dicts: [{"title": "...", "description": "...", "logo_url": "..."}, ...]"""
        return self._parse_json(self.brands_json)

    def get_testimonials(self):
        """Returns testimonials as a list of dicts: [{"title": "...", "description": "...", "client_name": "..."}, ...]"""
        return self._parse_json(self.testimonials_json)