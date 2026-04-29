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
    image       = models.ImageField(upload_to='about/strengths/', blank=True, null=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    class Meta:
        ordering = ['order', 'title']
    def __str__(self): return self.title

class Milestone(models.Model):
    year        = models.PositiveIntegerField()
    title       = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    image       = models.ImageField(upload_to='about/milestones/', blank=True, null=True)  # NEW
    tags        = models.CharField(max_length=500, blank=True,                             # NEW
                      help_text='Comma-separated tags e.g. Cement, Thrissur')
    order       = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['year', 'order']
    def __str__(self): return f'{self.year} – {self.title or self.description[:40]}'

    def tags_list(self):                                                                   # helper
        return [t.strip() for t in self.tags.split(',') if t.strip()]

class Project(models.Model):
    title            = models.CharField(max_length=255)
    description      = models.TextField()
    client           = models.CharField(max_length=255, blank=True)
    client_logo      = models.ImageField(upload_to='about/projects/logos/', blank=True, null=True)
    client_location  = models.CharField(max_length=255, blank=True)
    location         = models.CharField(max_length=255, blank=True)
    year             = models.PositiveIntegerField(null=True, blank=True)
    image            = models.ImageField(upload_to='about/projects/', blank=True, null=True)
    tag              = models.CharField(max_length=100, blank=True,
                           help_text='Badge shown on image e.g. PHASE 1, THRISSUR')
    contact_url      = models.URLField(blank=True, help_text='GET IN TOUCH link URL')
    is_featured      = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)
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

class TeamMember(models.Model):
    SOCIAL_PLATFORM_CHOICES = [
        ('facebook',  'Facebook'),
        ('linkedin',  'LinkedIn'),
        ('twitter',   'Twitter'),
        ('instagram', 'Instagram'),
    ]
    name            = models.CharField(max_length=255)
    role            = models.CharField(max_length=255)
    image           = models.ImageField(upload_to='about/team/', blank=True, null=True)
    social_platform = models.CharField(max_length=20, choices=SOCIAL_PLATFORM_CHOICES, blank=True)
    social_url      = models.URLField(blank=True)
    order           = models.PositiveIntegerField(default=0)
    is_active       = models.BooleanField(default=True)
    class Meta:
        ordering = ['order', 'name']
    def __str__(self): return f'{self.name} – {self.role}'

