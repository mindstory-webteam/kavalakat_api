from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from kavalakat.permissions import IsAdminOrReadOnly
from .models import Contact, Career, Enquiry
from .serializers import ContactSerializer, CareerSerializer, EnquiryPublicSerializer, EnquiryAdminSerializer

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class=ContactSerializer; permission_classes=[IsAdminOrReadOnly]; queryset=Contact.objects.all()
    def list(self, request, *args, **kwargs):
        obj=Contact.objects.first()
        return Response({'success':True,'data':self.get_serializer(obj).data if obj else None})
    def retrieve(self, request, *args, **kwargs):
        return Response({'success':True,'data':self.get_serializer(self.get_object()).data})
    def create(self, request, *args, **kwargs):
        s=self.get_serializer(data=request.data); s.is_valid(raise_exception=True); obj=s.save()
        return Response({'success':True,'message':'Contact created.','data':self.get_serializer(obj).data},status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        partial=kwargs.pop('partial',False)
        s=self.get_serializer(self.get_object(),data=request.data,partial=partial); s.is_valid(raise_exception=True); obj=s.save()
        return Response({'success':True,'message':'Contact updated.','data':self.get_serializer(obj).data})
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success':True,'message':'Deleted.'},status=status.HTTP_200_OK)

class CareerViewSet(viewsets.ModelViewSet):
    serializer_class=CareerSerializer; permission_classes=[IsAdminOrReadOnly]
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['job_type','is_active','department']; search_fields=['title','description','location']
    ordering_fields=['created_at','title','deadline']
    def get_queryset(self):
        qs=Career.objects.all()
        if not (self.request.user and self.request.user.is_staff): qs=qs.filter(is_active=True)
        return qs
    def list(self, request, *args, **kwargs):
        qs=self.filter_queryset(self.get_queryset()); page=self.paginate_queryset(qs)
        if page is not None: return self.get_paginated_response(self.get_serializer(page,many=True).data)
        return Response({'success':True,'count':qs.count(),'data':self.get_serializer(qs,many=True).data})
    def retrieve(self, request, *args, **kwargs):
        return Response({'success':True,'data':self.get_serializer(self.get_object()).data})
    def create(self, request, *args, **kwargs):
        s=self.get_serializer(data=request.data); s.is_valid(raise_exception=True); obj=s.save()
        return Response({'success':True,'message':'Career created.','data':self.get_serializer(obj).data},status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        partial=kwargs.pop('partial',False)
        s=self.get_serializer(self.get_object(),data=request.data,partial=partial); s.is_valid(raise_exception=True); obj=s.save()
        return Response({'success':True,'message':'Career updated.','data':self.get_serializer(obj).data})
    def destroy(self, request, *args, **kwargs):
        obj=self.get_object(); t=obj.title; obj.delete()
        return Response({'success':True,'message':f'Career "{t}" deleted.'}, status=status.HTTP_200_OK)
    @action(detail=True,methods=['post'],url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj=self.get_object(); obj.is_active=not obj.is_active; obj.save(update_fields=['is_active'])
        return Response({'success':True,'is_active':obj.is_active})

class EnquiryViewSet(viewsets.ModelViewSet):
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['status','enquiry_type']; search_fields=['name','email','subject','message']
    def get_queryset(self): return Enquiry.objects.all()
    def get_serializer_class(self):
        return EnquiryAdminSerializer if (self.request.user and self.request.user.is_staff) else EnquiryPublicSerializer
    def get_permissions(self):
        return [AllowAny()] if self.action=='create' else [IsAdminUser()]
    def list(self, request, *args, **kwargs):
        qs=self.filter_queryset(self.get_queryset()); page=self.paginate_queryset(qs)
        if page is not None: return self.get_paginated_response(self.get_serializer(page,many=True).data)
        return Response({'success':True,'count':qs.count(),'data':self.get_serializer(qs,many=True).data})
    def retrieve(self, request, *args, **kwargs):
        obj=self.get_object()
        if obj.status==Enquiry.STATUS_NEW and request.user.is_staff:
            obj.status=Enquiry.STATUS_READ; obj.save(update_fields=['status'])
        return Response({'success':True,'data':self.get_serializer(obj).data})
    def create(self, request, *args, **kwargs):
        s=EnquiryPublicSerializer(data=request.data); s.is_valid(raise_exception=True)
        ip=request.META.get('HTTP_X_FORWARDED_FOR','').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
        obj=s.save(ip_address=ip)
        return Response({'success':True,'message':'Thank you! We will get back to you within 24 hours.','data':EnquiryPublicSerializer(obj).data},status=status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        partial=kwargs.pop('partial',False)
        s=EnquiryAdminSerializer(self.get_object(),data=request.data,partial=partial); s.is_valid(raise_exception=True); obj=s.save()
        return Response({'success':True,'message':'Enquiry updated.','data':EnquiryAdminSerializer(obj).data})
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'success':True,'message':'Enquiry deleted.'},status=status.HTTP_200_OK)
    @action(detail=True,methods=['post'],url_path='mark-replied')
    def mark_replied(self, request, pk=None):
        obj=self.get_object(); obj.status=Enquiry.STATUS_REPLIED; obj.save(update_fields=['status'])
        return Response({'success':True,'status':obj.status})
    @action(detail=True,methods=['post'],url_path='mark-closed')
    def mark_closed(self, request, pk=None):
        obj=self.get_object(); obj.status=Enquiry.STATUS_CLOSED; obj.save(update_fields=['status'])
        return Response({'success':True,'status':obj.status})
    @action(detail=False,methods=['get'])
    def stats(self, request):
        data={r['status']:r['count'] for r in Enquiry.objects.values('status').annotate(count=Count('id'))}
        data['total']=Enquiry.objects.count()
        return Response({'success':True,'data':data})
