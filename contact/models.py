from django.db import models

class Contact(models.Model):
    phone=models.CharField(max_length=20); alt_phone=models.CharField(max_length=20,blank=True)
    email=models.EmailField(); alt_email=models.EmailField(blank=True)
    address=models.TextField(); city=models.CharField(max_length=100,blank=True)
    state=models.CharField(max_length=100,blank=True); pincode=models.CharField(max_length=10,blank=True)
    map_embed_url=models.URLField(blank=True); whatsapp=models.CharField(max_length=20,blank=True)
    facebook=models.URLField(blank=True); instagram=models.URLField(blank=True)
    linkedin=models.URLField(blank=True); youtube=models.URLField(blank=True)
    business_hours=models.TextField(blank=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name='Contact Info'; verbose_name_plural='Contact Info'
    def __str__(self): return f'Contact – {self.email}'

class Career(models.Model):
    JOB_TYPES=[('Full-Time','Full-Time'),('Part-Time','Part-Time'),('Contract','Contract'),('Internship','Internship')]
    title=models.CharField(max_length=255); department=models.CharField(max_length=100,blank=True)
    description=models.TextField(); requirements=models.TextField(blank=True)
    location=models.CharField(max_length=255,blank=True)
    job_type=models.CharField(max_length=50,choices=JOB_TYPES,default='Full-Time')
    experience=models.CharField(max_length=100,blank=True); salary_range=models.CharField(max_length=100,blank=True)
    is_active=models.BooleanField(default=True); deadline=models.DateField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self): return self.title

class Enquiry(models.Model):
    STATUS_NEW='new'; STATUS_READ='read'; STATUS_REPLIED='replied'; STATUS_CLOSED='closed'
    STATUS_CHOICES=[(STATUS_NEW,'New'),(STATUS_READ,'Read'),(STATUS_REPLIED,'Replied'),(STATUS_CLOSED,'Closed')]
    TYPE_CHOICES=[('general','General'),('career','Career'),('quote','Quote'),('support','Support')]
    name=models.CharField(max_length=255); email=models.EmailField()
    phone=models.CharField(max_length=20,blank=True); company=models.CharField(max_length=255,blank=True)
    subject=models.CharField(max_length=255,blank=True); message=models.TextField()
    enquiry_type=models.CharField(max_length=20,choices=TYPE_CHOICES,default='general')
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default=STATUS_NEW)
    admin_note=models.TextField(blank=True); ip_address=models.GenericIPAddressField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self): return f'[{self.get_status_display()}] {self.name}'
