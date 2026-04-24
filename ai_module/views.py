import logging
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import AIGenerationLog
from .serializers import GenerateBlogInputSerializer, AIGenerationLogSerializer
from .services import generate_blog_content
logger = logging.getLogger('ai_module')

class GenerateBlogView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        inp = GenerateBlogInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        topic=inp.validated_data['topic']; save_as_draft=inp.validated_data.get('save_as_draft',False)
        category_id=inp.validated_data.get('category_id'); author_id=inp.validated_data.get('author_id')
        log=AIGenerationLog.objects.create(topic=topic,status='pending',requested_by=request.user)
        try: result=generate_blog_content(topic)
        except (ValueError,RuntimeError) as exc:
            log.status='failed'; log.error_message=str(exc); log.save(update_fields=['status','error_message'])
            return Response({'success':False,'message':str(exc)},status=status.HTTP_502_BAD_GATEWAY)
        log.generated_title=result['title']; log.generated_excerpt=result['excerpt']
        log.generated_content=result['content']; log.model_used=result['model_used']
        log.tokens_used=result['tokens_used']; log.status='success'; log.save()
        post_id=None; post_slug=None
        if save_as_draft:
            try:
                post=_save_post(result,topic,category_id,author_id,request.user)
                log.saved_as_post=True; log.blog_post=post; log.save(update_fields=['saved_as_post','blog_post'])
                post_id=post.pk; post_slug=post.slug
            except Exception as exc: logger.warning('Could not save post: %s',exc)
        return Response({'success':True,'data':{
            'log_id':log.pk,'topic':topic,'title':result['title'],'excerpt':result['excerpt'],
            'content':result['content'],'tags':result.get('tags',''),
            'meta_title':result.get('meta_title',''),'meta_description':result.get('meta_description',''),
            'model_used':result['model_used'],'tokens_used':result['tokens_used'],
            'saved_as_post':log.saved_as_post,'post_id':post_id,'post_slug':post_slug,
        }},status=status.HTTP_200_OK)

def _save_post(result,topic,category_id,author_id,user):
    from blog.models import Post, Category as BlogCategory
    from django.contrib.auth import get_user_model
    from django.utils.text import slugify
    User=get_user_model(); category=None; author=user
    if category_id:
        try: category=BlogCategory.objects.get(pk=category_id)
        except: pass
    if author_id:
        try: author=User.objects.get(pk=author_id)
        except: pass
    base=slugify(result['title']); slug=base; n=1
    from blog.models import Post
    while Post.objects.filter(slug=slug).exists(): slug=f'{base}-{n}'; n+=1
    return Post.objects.create(
        title=result['title'],slug=slug,excerpt=result['excerpt'],content=result['content'],
        tags=result.get('tags',topic),meta_title=result.get('meta_title',''),
        meta_description=result.get('meta_description',''),
        category=category,author=author,status=Post.STATUS_DRAFT,is_ai_generated=True,
    )

class AIGenerationLogViewSet(viewsets.ModelViewSet):
    serializer_class=AIGenerationLogSerializer; permission_classes=[IsAdminUser]
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['status','saved_as_post','model_used']
    search_fields=['topic','generated_title','requested_by__username']
    ordering_fields=['created_at','tokens_used']
    def get_queryset(self): return AIGenerationLog.objects.select_related('requested_by','blog_post').all()
    def list(self, request, *args, **kwargs):
        qs=self.filter_queryset(self.get_queryset()); page=self.paginate_queryset(qs)
        if page is not None: return self.get_paginated_response(self.get_serializer(page,many=True).data)
        return Response({'success':True,'count':qs.count(),'data':self.get_serializer(qs,many=True).data})
    def retrieve(self, request, *args, **kwargs):
        return Response({'success':True,'data':self.get_serializer(self.get_object()).data})
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success':True,'message':'Log deleted.'},status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        return Response({'success':False,'message':'Logs are system-generated.'},status=405)
    def update(self, request, *args, **kwargs):
        return Response({'success':False,'message':'Logs are read-only.'},status=405)
