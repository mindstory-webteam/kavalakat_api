from django.db import models

class About(models.Model):
    title          = models.CharField(max_length=255)
    description    = models.TextField()
    vision         = models.TextField(blank=True)
    mission        = models.TextField(blank=True)
    founded_year   = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    updated_at     = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About'
    def __str__(self): return self.title

class Strength(models.Model):
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    class Meta:
        ordering = ['order', 'title']
    def __str__(self): return self.title

class Milestone(models.Model):
    year        = models.PositiveIntegerField()
    title       = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    order       = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['year', 'order']
    def __str__(self): return f'{self.year} – {self.title or self.description[:40]}'

class Project(models.Model):
    title       = models.CharField(max_length=255)
    description = models.TextField()
    client      = models.CharField(max_length=255, blank=True)
    location    = models.CharField(max_length=255, blank=True)
    year        = models.PositiveIntegerField(null=True, blank=True)
    image       = models.ImageField(upload_to='about/projects/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self): return self.title

class Gallery(models.Model):
    title      = models.CharField(max_length=255, blank=True)
    image      = models.ImageField(upload_to='about/gallery/')
    caption    = models.TextField(blank=True)
    order      = models.PositiveIntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['order', '-created_at']
    def __str__(self): return self.title or f'Gallery #{self.pk}'
