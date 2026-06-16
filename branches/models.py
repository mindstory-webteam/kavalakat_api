from django.db import models

from kavalakat.validators import validate_image_file


class BranchLocation(models.Model):
    """A physical branch / office location shown on the Contact Us page."""

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    branch_name = models.CharField(max_length=150)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    google_map_link = models.URLField(blank=True, help_text='Google Maps share / embed link')
    location_image = models.ImageField(
        upload_to='branches/locations/',
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text='JPG, JPEG, PNG or WEBP. Max size 5 MB.',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['branch_name']
        verbose_name = 'Branch Location'
        verbose_name_plural = 'Branch Locations'

    def __str__(self):
        return self.branch_name

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE
