"""
Shared image validation helpers used by Events and ContactLocation models.
Allowed formats: JPG, JPEG, PNG, WEBP  |  Max size: 5 MB
"""
import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

ALLOWED_EXTENSIONS   = ['.jpg', '.jpeg', '.png', '.webp']
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
MAX_MB = 5


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'Unsupported format "{ext}". Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        )


def validate_image_content_type(value):
    ct = getattr(value, 'content_type', None)
    if ct and ct not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            f'Unsupported MIME type "{ct}". Allowed: JPG, JPEG, PNG, WEBP'
        )


def validate_image_size(value, max_mb=MAX_MB):
    size = getattr(value, 'size', 0)
    if size and size > max_mb * 1024 * 1024:
        raise ValidationError(
            f'File too large ({filesizeformat(size)}). Max allowed: {filesizeformat(max_mb * 1024 * 1024)}'
        )


def validate_image_file(value):
    """Single validator for ImageField — combines extension + mime + size."""
    validate_image_extension(value)
    validate_image_content_type(value)
    validate_image_size(value)
