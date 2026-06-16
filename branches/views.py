from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from kavalakat.permissions import IsAdminOrReadOnly
from .models import BranchLocation
from .serializers import BranchLocationSerializer


class BranchLocationViewSet(viewsets.ModelViewSet):
    """
    GET    /api/branches/                list branch locations (paginated)
    POST   /api/branches/                create  (admin)
    GET    /api/branches/<id>/           retrieve a single branch
    PUT    /api/branches/<id>/           update  (admin)
    PATCH  /api/branches/<id>/           partial update (admin)
    DELETE /api/branches/<id>/           delete  (admin)
    POST   /api/branches/<id>/toggle-status/  flip active/inactive (admin)

    Filter:  ?status=active|inactive
    Search:  ?search=keyword (branch_name, address, phone_number, email)
    Order:   ?ordering=branch_name | -created_at ...
    """
    serializer_class = BranchLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['branch_name', 'address', 'phone_number', 'email']
    ordering_fields = ['branch_name', 'created_at', 'updated_at']
    ordering = ['branch_name']

    def get_queryset(self):
        qs = BranchLocation.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(status=BranchLocation.STATUS_ACTIVE)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response({'success': True, 'count': qs.count(),
                          'data': self.get_serializer(qs, many=True).data})

    def retrieve(self, request, *args, **kwargs):
        return Response({'success': True, 'data': self.get_serializer(self.get_object()).data})

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response(
            {'success': True, 'message': 'Branch location created.', 'data': self.get_serializer(obj).data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        s = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({'success': True, 'message': 'Branch location updated.', 'data': self.get_serializer(obj).data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.branch_name
        obj.delete()
        return Response({'success': True, 'message': f'"{name}" deleted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-status', permission_classes=[IsAdminOrReadOnly])
    def toggle_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = (
            BranchLocation.STATUS_INACTIVE if obj.status == BranchLocation.STATUS_ACTIVE
            else BranchLocation.STATUS_ACTIVE
        )
        obj.save(update_fields=['status'])
        return Response({'success': True, 'status': obj.status})
