from django.db import models


# ── Service Category ─────────────────────────────────────────────────────────
class ServiceCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True, help_text='FontAwesome class e.g. fa-solid fa-building')
    color       = models.CharField(max_length=20, blank=True, default='#0284f0', help_text='Hex color for badge e.g. #f97316')
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ── Top-level Service (category) ─────────────────────────────────────────────
class Service(models.Model):
    name        = models.CharField(max_length=255)
    category    = models.ForeignKey('ServiceCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    slug        = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True, help_text='FontAwesome class')
    image       = models.ImageField(upload_to='services/list/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Service'

    def __str__(self):
        return self.name


# ── 1. About Section (per service) ───────────────────────────────────────────
class ServiceAbout(models.Model):
    service          = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='about')
    main_title       = models.CharField(max_length=255)
    sub_title        = models.CharField(max_length=255, blank=True)
    description      = models.TextField(blank=True)
    left_side_image  = models.ImageField(upload_to='services/about/', blank=True, null=True)
    gallery_image_1  = models.ImageField(upload_to='services/about/gallery/', blank=True, null=True)
    gallery_image_2  = models.ImageField(upload_to='services/about/gallery/', blank=True, null=True)
    gallery_image_3  = models.ImageField(upload_to='services/about/gallery/', blank=True, null=True)
    button_text      = models.CharField(max_length=100, blank=True)
    button_link      = models.CharField(max_length=500, blank=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service About Section'

    def __str__(self):
        return f'{self.service.name} – About'


# ── 2. Counter / Statistics (per service) ────────────────────────────────────
class ServiceCounter(models.Model):
    service           = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='counters')
    counter_title     = models.CharField(max_length=255)
    counter_number    = models.CharField(max_length=50, help_text='e.g. 4+, 100%, 24/7, 5★')
    short_description = models.CharField(max_length=255, blank=True)
    icon              = models.CharField(max_length=100, blank=True, help_text='FontAwesome class e.g. fa-solid fa-star')
    order             = models.PositiveIntegerField(default=0)
    is_active         = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'counter_title']
        verbose_name = 'Service Counter'

    def __str__(self):
        return f'{self.service.name} – {self.counter_number} {self.counter_title}'


# ── 3. What We Offer (per service) ───────────────────────────────────────────
class ServiceOffer(models.Model):
    service           = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='offers')
    offer_title       = models.CharField(max_length=255)
    offer_icon        = models.CharField(max_length=100, blank=True, help_text='FontAwesome class e.g. fa-solid fa-wifi')
    short_description = models.CharField(max_length=500, blank=True)
    order             = models.PositiveIntegerField(default=0)
    is_active         = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'offer_title']
        verbose_name = 'Service Offer'

    def __str__(self):
        return f'{self.service.name} – {self.offer_title}'


# ── 4. Features / FAQ (per service) ──────────────────────────────────────────
class ServiceFeatureSection(models.Model):
    service          = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='feature_section')
    section_title    = models.CharField(max_length=255)
    left_main_image  = models.ImageField(upload_to='services/features/', blank=True, null=True)
    main_description = models.TextField(blank=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Feature Section'

    def __str__(self):
        return f'{self.service.name} – Features'


class ServiceFeature(models.Model):
    section             = models.ForeignKey(ServiceFeatureSection, on_delete=models.CASCADE, related_name='features')
    feature_title       = models.CharField(max_length=255)
    feature_description = models.TextField(blank=True)
    order               = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'feature_title']
        verbose_name = 'Service Feature'

    def __str__(self):
        return self.feature_title


# ── 5. Highlights Video (per service) ────────────────────────────────────────
class ServiceHighlight(models.Model):
    service               = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='highlights')
    section_title         = models.CharField(max_length=255, blank=True)
    section_sub_title     = models.CharField(max_length=255, blank=True)
    highlight_title       = models.CharField(max_length=255)
    highlight_description = models.TextField(blank=True)
    highlight_video       = models.FileField(upload_to='services/videos/', blank=True, null=True)
    display_order         = models.PositiveIntegerField(default=0)
    is_active             = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'highlight_title']
        verbose_name = 'Service Highlight'

    def __str__(self):
        return f'{self.service.name} – {self.highlight_title}'


# ── 6. Location Advantages (per service) ─────────────────────────────────────
class ServiceLocation(models.Model):
    service                   = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='location')
    location_main_title       = models.CharField(max_length=255)
    location_main_sub_title   = models.CharField(max_length=255, blank=True)
    location_main_description = models.TextField(blank=True)
    left_main_image           = models.ImageField(upload_to='services/location/', blank=True, null=True)
    updated_at                = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Location Section'

    def __str__(self):
        return f'{self.service.name} – Location'


class ServiceNearbyPlace(models.Model):
    location          = models.ForeignKey(ServiceLocation, on_delete=models.CASCADE, related_name='nearby_places')
    nearby_place_name = models.CharField(max_length=255)
    distance          = models.CharField(max_length=100, blank=True, help_text='e.g. 2 km, 500 m')
    map_link          = models.URLField(blank=True)
    order             = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'nearby_place_name']
        verbose_name = 'Nearby Place'

    def __str__(self):
        return f'{self.nearby_place_name} ({self.distance})'
