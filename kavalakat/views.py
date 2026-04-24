from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone


class APIRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        base = request.build_absolute_uri('/api/')
        return Response({
            'success': True,
            'message': 'Kavalakat API v2',
            'endpoints': {
                'auth':            f'{base}auth/token/',
                'pages':           f'{base}pages/',
                'about':           f'{base}about/',
                'strengths':       f'{base}strengths/',
                'milestones':      f'{base}milestones/',
                'projects':        f'{base}projects/',
                'gallery':         f'{base}gallery/',
                'portfolio':       f'{base}portfolio/',
                'portfolio_items': f'{base}portfolio-items/',
                'blog':            f'{base}blog/',
                'blog_categories': f'{base}blog/categories/',
                'contact':         f'{base}contact/',
                'careers':         f'{base}careers/',
                'enquiry':         f'{base}enquiry/',
                'ai_generate':     f'{base}ai/generate-blog/',
                'ai_logs':         f'{base}ai/logs/',
                'health':          f'{base}health/',
            },
        })


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection
        try:
            connection.ensure_connection()
            db = 'ok'
        except Exception:
            db = 'error'
        return Response({'success': True, 'status': 'healthy', 'database': db,
                         'timestamp': timezone.now().isoformat()})
