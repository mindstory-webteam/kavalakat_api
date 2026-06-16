from rest_framework import serializers
from django.utils import timezone
from .models import Contact, ContactLocation, Career, JobApplication, Enquiry


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


class ContactLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ContactLocation
        fields = [
            'id', 'branch_name', 'address', 'phone_number', 'whatsapp',
            'email', 'google_map_link', 'working_hours',
            'display_order', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_branch_name(self, v):
        v = v.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Branch name must be at least 2 characters.')
        return v

    def validate_phone_number(self, v):
        if not v:
            return v
        digits = ''.join(c for c in v if c.isdigit())
        if digits and len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return v.strip()

    def validate_whatsapp(self, v):
        if not v:
            return v
        digits = ''.join(c for c in v if c.isdigit())
        if digits and len(digits) < 7:
            raise serializers.ValidationError('Enter a valid WhatsApp number.')
        return v.strip()


class CareerSerializer(serializers.ModelSerializer):
    is_expired        = serializers.SerializerMethodField(read_only=True)
    application_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Career
        fields = [
            'id', 'title', 'department', 'description', 'requirements',
            'location', 'job_type', 'experience', 'salary_range',
            'is_active', 'deadline', 'is_expired',
            'application_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'application_count']

    def get_is_expired(self, obj):
        if obj.deadline:
            return obj.deadline < timezone.now().date()
        return False

    def get_application_count(self, obj):
        return obj.applications.count()


class JobApplicationPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = JobApplication
        fields = ['id', 'career', 'name', 'email', 'phone',
                  'resume', 'cover_letter', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_name(self, v):
        v = v.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Full name must be at least 2 characters.')
        return v

    def validate_phone(self, v):
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return v.strip()

    def validate_cover_letter(self, v):
        v = v.strip()
        if len(v) < 10:
            raise serializers.ValidationError('Cover letter must be at least 10 characters.')
        return v

    def validate_resume(self, v):
        if not v.name.lower().endswith('.pdf'):
            raise serializers.ValidationError('Only PDF files are accepted.')
        if v.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Resume must be under 5 MB.')
        return v


class JobApplicationAdminSerializer(serializers.ModelSerializer):
    career_title = serializers.CharField(source='career.title', read_only=True, default=None)
    resume_url   = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = JobApplication
        fields = [
            'id', 'career', 'career_title', 'name', 'email', 'phone',
            'resume', 'resume_url', 'cover_letter',
            'status', 'admin_note', 'ip_address', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at',
                            'resume_url', 'career_title']

    def get_resume_url(self, obj):
        if obj.resume:
            req = self.context.get('request')
            return req.build_absolute_uri(obj.resume.url) if req else obj.resume.url
        return None


class EnquiryPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = ['id', 'name', 'email', 'phone', 'subject',
                  'message', 'terms_accepted', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_name(self, v):
        v = v.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return v

    def validate_phone(self, v):
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) < 7:
            raise serializers.ValidationError('Enter a valid phone number.')
        return v.strip()

    def validate_message(self, v):
        v = v.strip()
        if len(v) < 10:
            raise serializers.ValidationError('Message must be at least 10 characters.')
        return v

    def validate_terms_accepted(self, v):
        if not v:
            raise serializers.ValidationError('You must accept the Terms & Conditions.')
        return v


class EnquiryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject',
            'message', 'terms_accepted',
            'status', 'admin_note', 'ip_address', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'ip_address', 'created_at', 'updated_at']
