from rest_framework import serializers
from .models import Contact, Career, Enquiry

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact
        fields=['id','phone','alt_phone','email','alt_email','address','city','state','pincode',
                'map_embed_url','whatsapp','facebook','instagram','linkedin','youtube','business_hours','updated_at']
        read_only_fields=['id','updated_at']

class CareerSerializer(serializers.ModelSerializer):
    is_expired=serializers.SerializerMethodField()
    class Meta:
        model=Career
        fields=['id','title','department','description','requirements','location','job_type',
                'experience','salary_range','is_active','deadline','is_expired','created_at','updated_at']
        read_only_fields=['id','created_at','updated_at']
    def get_is_expired(self, obj):
        if obj.deadline:
            from django.utils import timezone
            return obj.deadline < timezone.now().date()
        return False

class EnquiryPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enquiry
        fields=['id','name','email','phone','company','subject','message','enquiry_type','created_at']
        read_only_fields=['id','created_at']
    def validate_name(self, v):
        if len(v.strip())<2: raise serializers.ValidationError('Name too short.')
        return v.strip()
    def validate_message(self, v):
        if len(v.strip())<10: raise serializers.ValidationError('Message must be at least 10 characters.')
        return v.strip()

class EnquiryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enquiry
        fields=['id','name','email','phone','company','subject','message','enquiry_type',
                'status','admin_note','ip_address','created_at','updated_at']
        read_only_fields=['id','ip_address','created_at','updated_at']
