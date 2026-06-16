from django.db import models
from django.utils.text import slugify

from kavalakat.validators import validate_image_file


class EventCategory(models.Model):
    """
    Event categories — Expo, Workshop, CSR, Networking …
    Each category has its own detail page on the frontend.
    """
    STATUS_ACTIVE   = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES  = [(STATUS_ACTIVE, 'Active'), (STATUS_INACTIVE, 'Inactive')]

    name        = models.CharField(max_length=150, unique=True,
                                   verbose_name='Category Name')
    slug        = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True,
                                   help_text='Shown on the category detail page')
    icon        = models.CharField(max_length=80, blank=True,
                                   help_text='Font Awesome class e.g. fa-calendar-star')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES,
                                   default=STATUS_ACTIVE)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['name']
        verbose_name        = 'Event Category'
        verbose_name_plural = 'Event Categories'

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:160] or 'category'
            slug, n = base, 1
            while EventCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1; slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)


class Event(models.Model):
    """
    Full event record.
    status is draft / published — only published events are visible to the public.
    """
    STATUS_DRAFT     = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES   = [
        (STATUS_DRAFT,     'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    # ── Core ─────────────────────────────────────────────────────────────────
    event_name        = models.CharField(max_length=255, verbose_name='Event Name')
    slug              = models.SlugField(max_length=280, unique=True, blank=True)
    short_description = models.CharField(
        max_length=500, blank=True,
        help_text='Brief teaser shown on event cards',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Full Description',
        help_text='Full event details shown in popup / detail page',
    )
    is_featured = models.BooleanField(default=False, db_index=True,
                                      help_text='Featured events appear first')
    status      = models.CharField(max_length=12, choices=STATUS_CHOICES,
                                   default=STATUS_DRAFT, db_index=True)

    # ── Category ─────────────────────────────────────────────────────────────
    category = models.ForeignKey(
        EventCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='events',
        verbose_name='Event Category',
    )
    tag = models.CharField(
        max_length=80, blank=True,
        help_text='Pill label on card e.g. Expo, Workshop. Auto-filled from category.',
    )

    # ── Primary image ─────────────────────────────────────────────────────────
    featured_image = models.ImageField(
        upload_to='events/featured/', blank=True, null=True,
        validators=[validate_image_file],
        help_text='Card thumbnail — JPG/JPEG/PNG/WEBP max 5 MB',
    )

    # ── Organiser ─────────────────────────────────────────────────────────────
    organizer      = models.CharField(max_length=255, blank=True)
    organizer_logo = models.ImageField(
        upload_to='events/organizer_logos/', blank=True, null=True,
        validators=[validate_image_file],
        help_text='JPG/JPEG/PNG/WEBP max 5 MB',
    )

    # ── Schedule / venue ─────────────────────────────────────────────────────
    event_date = models.DateTimeField(db_index=True, verbose_name='Event Date')
    event_time = models.CharField(max_length=100, blank=True,
                                  help_text='e.g. 10:00 AM – 6:00 PM')
    venue      = models.CharField(max_length=255, blank=True,
                                  help_text='Venue name')
    location   = models.CharField(max_length=255, blank=True,
                                  help_text='City / full address')

    # ── Registration ─────────────────────────────────────────────────────────
    registration_url = models.CharField(
        max_length=500, blank=True,
        verbose_name='Registration Link',
        help_text='Full URL or relative path e.g. /contact',
    )

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['-is_featured', '-event_date']
        verbose_name        = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.event_name

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.event_date >= timezone.now()

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.event_name)[:260] or 'event'
            slug, n = base, 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1; slug = f'{base}-{n}'
            self.slug = slug
        if not self.tag and self.category_id:
            try:
                self.tag = EventCategory.objects.get(pk=self.category_id).name
            except EventCategory.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class EventImage(models.Model):
    """Gallery images for an event (multiple per event)."""
    event       = models.ForeignKey(Event, on_delete=models.CASCADE,
                                    related_name='gallery_images')
    image       = models.ImageField(
        upload_to='events/gallery/',
        validators=[validate_image_file],
        help_text='JPG/JPEG/PNG/WEBP max 5 MB',
    )
    caption     = models.CharField(max_length=200, blank=True)
    order       = models.PositiveSmallIntegerField(default=0,
                                                    help_text='Lower = first')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['order', 'uploaded_at']
        verbose_name        = 'Event Gallery Image'
        verbose_name_plural = 'Event Gallery Images'

    def __str__(self):
        return f'{self.event.event_name} — image {self.pk}'
