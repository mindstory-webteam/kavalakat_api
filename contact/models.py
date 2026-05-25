from django.db import models


# ── Contact Info (single record) ─────────────────────────────────────────────
class Contact(models.Model):
    phone          = models.CharField(max_length=20)
    alt_phone      = models.CharField(max_length=20, blank=True)
    email          = models.EmailField()
    alt_email      = models.EmailField(blank=True)
    address        = models.TextField()
    city           = models.CharField(max_length=100, blank=True)
    state          = models.CharField(max_length=100, blank=True)
    pincode        = models.CharField(max_length=10, blank=True)
    map_embed_url  = models.URLField(blank=True)
    whatsapp       = models.CharField(max_length=20, blank=True)
    facebook       = models.URLField(blank=True)
    instagram      = models.URLField(blank=True)
    linkedin       = models.URLField(blank=True)
    youtube        = models.URLField(blank=True)
    business_hours = models.TextField(blank=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Contact Info'
        verbose_name_plural = 'Contact Info'

    def __str__(self):
        return f'Contact – {self.email}'


# ── Career / Job Posting ──────────────────────────────────────────────────────
class Career(models.Model):
    JOB_TYPES = [
        ('Full-Time',  'Full-Time'),
        ('Part-Time',  'Part-Time'),
        ('Contract',   'Contract'),
        ('Internship', 'Internship'),
    ]
    title        = models.CharField(max_length=255)
    department   = models.CharField(max_length=100, blank=True)
    description  = models.TextField()
    requirements = models.TextField(blank=True)
    location     = models.CharField(max_length=255, blank=True)
    job_type     = models.CharField(max_length=50, choices=JOB_TYPES, default='Full-Time')
    experience   = models.CharField(max_length=100, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    is_active    = models.BooleanField(default=True)
    deadline     = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ── Enquiry / Contact Form Submission ─────────────────────────────────────────
class Enquiry(models.Model):
    # Status constants
    STATUS_NEW     = 'new'
    STATUS_READ    = 'read'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED  = 'closed'
    STATUS_CHOICES = [
        (STATUS_NEW,     'New'),
        (STATUS_READ,    'Read'),
        (STATUS_REPLIED, 'Replied'),
        (STATUS_CLOSED,  'Closed'),
    ]

    # Form fields matching the frontend form
    name    = models.CharField(max_length=255, verbose_name='Full Name')
    email   = models.EmailField(verbose_name='Email')
    phone   = models.CharField(max_length=20, verbose_name='Phone')
    subject = models.CharField(max_length=255, blank=True, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')

    # Terms & Conditions acceptance
    terms_accepted = models.BooleanField(default=False, verbose_name='Terms & Conditions Accepted')

    # Admin / internal fields
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_note = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['-created_at']
        verbose_name = 'Enquiry'

    def __str__(self):
        return f'[{self.get_status_display()}] {self.name} — {self.email}'