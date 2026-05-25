from rest_framework import serializers
from .models import Contact, Career, Enquiry


# ── Contact Info ──────────────────────────────────────────────────────────────
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Contact
        fields = [
            'id', 'phone', 'alt_phone', 'email', 'alt_email',
            'address', 'city', 'state', 'pincode',
            'map_embed_url', 'whatsapp',
            'facebook', 'instagram', 'linkedin', 'youtube',
            'business_hours', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


# ── Career ────────────────────────────────────────────────────────────────────
class CareerSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Career
        fields = [
            'id', 'title', 'department', 'description', 'requirements',
            'location', 'job_type', 'experience', 'salary_range',
            'is_active', 'deadline', 'is_expired',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired']

    def get_is_expired(self, obj):
        if obj.deadline:
            from django.utils import timezone
            return obj.deadline < timezone.now().date()
        return False


# ── Enquiry — Public (what the frontend contact form submits) ─────────────────
class EnquiryPublicSerializer(serializers.ModelSerializer):
    """
    Used for POST /api/enquiry/  (public contact form submission).

    Required fields  : name, email, phone, message, terms_accepted
    Optional fields  : subject
    Read-only        : id, status, created_at

    Frontend form fields:
        Full Name *   → name
        Email *       → email
        Phone *       → phone
        Subject       → subject
        Message *     → message
        Terms & Cond* → terms_accepted
    """

    class Meta:
        model  = Enquiry
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'subject',
            'message',
            'terms_accepted',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    # ── Validation ─────────────────────────────────────────────────────────
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Full name must be at least 2 characters.')
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Phone number is required.')
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Message must be at least 10 characters.')
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                'You must accept the Terms & Conditions to submit this form.'
            )
        return value


# ── Enquiry — Admin (full data for dashboard) ─────────────────────────────────
class EnquiryAdminSerializer(serializers.ModelSerializer):
    """
    Used by admin endpoints — includes status, admin_note, ip_address.
    """

    class Meta:
        model  = Enquiry
        fields = [
            'id',
            'name', 'email', 'phone', 'subject', 'message',
            'terms_accepted',
            'status', 'admin_note',
            'ip_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at']