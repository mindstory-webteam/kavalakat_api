from django.db import models


# ── Contact Info ──────────────────────────────────────────────────────────────
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


# ── Job Application ───────────────────────────────────────────────────────────
class JobApplication(models.Model):
    STATUS_NEW         = 'new'
    STATUS_REVIEWED    = 'reviewed'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED    = 'rejected'
    STATUS_HIRED       = 'hired'
    STATUS_CHOICES = [
        ('new',         'New'),
        ('reviewed',    'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected',    'Rejected'),
        ('hired',       'Hired'),
    ]

    career       = models.ForeignKey(Career, on_delete=models.SET_NULL,
                       null=True, blank=True, related_name='applications')
    name         = models.CharField(max_length=255)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20)
    resume       = models.FileField(upload_to='applications/resumes/')
    cover_letter = models.TextField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_note   = models.TextField(blank=True)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Job Application'

    def __str__(self):
        job = self.career.title if self.career else 'General'
        return f'{self.name} → {job}'


# ── Enquiry ───────────────────────────────────────────────────────────────────
class Enquiry(models.Model):
    STATUS_NEW     = 'new'
    STATUS_READ    = 'read'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED  = 'closed'
    STATUS_CHOICES = [
        ('new',     'New'),
        ('read',    'Read'),
        ('replied', 'Replied'),
        ('closed',  'Closed'),
    ]

    name           = models.CharField(max_length=255)
    email          = models.EmailField()
    phone          = models.CharField(max_length=20)
    subject        = models.CharField(max_length=255, blank=True)
    message        = models.TextField()
    terms_accepted = models.BooleanField(default=False)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_note     = models.TextField(blank=True)
    ip_address     = models.GenericIPAddressField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Enquiry'

    def __str__(self):
        return f'[{self.get_status_display()}] {self.name}'
