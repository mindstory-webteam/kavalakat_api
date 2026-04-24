from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    TRADING      = 'Trading'
    DISTRIBUTION = 'Distribution'
    SERVICES     = 'Services'
    CHOICES = [
        (TRADING,      'Trading'),
        (DISTRIBUTION, 'Distribution'),
        (SERVICES,     'Services'),
    ]

    name        = models.CharField(max_length=100, choices=CHOICES, unique=True)
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
    category    = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='items'
    )
    name        = models.CharField(
        max_length=255,
        help_text='Displayed in UPPERCASE on the website'
    )
    description = models.TextField(blank=True)
    image       = models.ImageField(
        upload_to='portfolio/items/', blank=True, null=True
    )
    tags        = models.CharField(
        max_length=255, blank=True,
        help_text='Comma-separated keywords'
    )
    is_featured = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['order', 'name']
        verbose_name        = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def save(self, *args, **kwargs):
        self.name = self.name.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} [{self.category.name}]'