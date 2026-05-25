from rest_framework import serializers
from .models import Contact, Career, JobApplication, Enquiry


# ── Contact ───────────────────────────────────────────────────────────────────
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
    is_expired         = serializers.SerializerMethodField(read_only=True)
    application_count  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Career
        fields = [
            'id', 'title', 'department', 'description', 'requirements',
            'location', 'job_type', 'experience', 'salary_range',
            'is_active', 'deadline', 'is_expired',
            'application_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'application_count']

    def get_is_expired(self, obj):
        if obj.deadline:
            from django.utils import timezone
            return obj.deadline < timezone.now().date()
        return False

    def get_application_count(self, obj):
        return obj.applications.count()


# ── Job Application — Public (what applicant submits) ─────────────────────────
class JobApplicationPublicSerializer(serializers.ModelSerializer):
    """
    Frontend form fields:
        Full Name *        → name
        Email *            → email
        Phone *            → phone
        Upload Resume *    → resume  (PDF file)
        Cover Letter *     → cover_letter
    Optional:
        career             → career (FK — pass career id or omit)
    """

    class Meta:
        model  = JobApplication
        fields = ['id', 'career', 'name', 'email', 'phone',
                  'resume', 'cover_letter', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Full name must be at least 2 characters.')
        return value

    def validate_phone(self, value):
        value = value.strip()
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate_cover_letter(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Cover letter must be at least 10 characters.')
        return value

    def validate_resume(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError('Only PDF files are accepted.')
        if value.size > 5 * 1024 * 1024:  # 5 MB limit
            raise serializers.ValidationError('Resume file must be under 5 MB.')
        return value


# ── Job Application — Admin (full data) ───────────────────────────────────────
class JobApplicationAdminSerializer(serializers.ModelSerializer):
    career_title = serializers.CharField(source='career.title', read_only=True, default=None)
    resume_url   = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = JobApplication
        fields = [
            'id', 'career', 'career_title',
            'name', 'email', 'phone',
            'resume', 'resume_url',
            'cover_letter',
            'status', 'admin_note',
            'ip_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at', 'resume_url', 'career_title']

    def get_resume_url(self, obj):
        if obj.resume:
            req = self.context.get('request')
            return req.build_absolute_uri(obj.resume.url) if req else obj.resume.url
        return None


# ── Enquiry — Public ──────────────────────────────────────────────────────────
class EnquiryPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = ['id', 'name', 'email', 'phone', 'subject',
                  'message', 'terms_accepted', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value

    def validate_phone(self, value):
        value = value.strip()
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
                'You must accept the Terms & Conditions.')
        return value


# ── Enquiry — Admin ───────────────────────────────────────────────────────────
class EnquiryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject',
            'message', 'terms_accepted',
            'status', 'admin_note',
            'ip_address', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at']
