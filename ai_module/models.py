from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class AIGenerationLog(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('success','Success'),('failed','Failed')]
    topic=models.CharField(max_length=500); generated_title=models.CharField(max_length=500,blank=True)
    generated_content=models.TextField(blank=True); generated_excerpt=models.TextField(blank=True)
    model_used=models.CharField(max_length=100,default='gpt-4o-mini')
    tokens_used=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    error_message=models.TextField(blank=True)
    requested_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='ai_logs')
    saved_as_post=models.BooleanField(default=False)
    blog_post=models.ForeignKey('blog.Post',on_delete=models.SET_NULL,null=True,blank=True,related_name='ai_logs')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self): return f'[{self.status}] {self.topic[:50]}'
