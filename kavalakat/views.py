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
                # ── Auth ──────────────────────────────────────
                'auth_token':         f'{base}auth/token/',
                'auth_refresh':       f'{base}auth/token/refresh/',
                'auth_verify':        f'{base}auth/token/verify/',

                # ── Pages ─────────────────────────────────────
                'pages':              f'{base}pages/',

                # ── About ─────────────────────────────────────
                'about':              f'{base}about/',
                'strengths':          f'{base}strengths/',
                'milestones':         f'{base}milestones/',
                'projects':           f'{base}projects/',
                'gallery':            f'{base}gallery/',
                'team':               f'{base}team/',

                # ── Portfolio ─────────────────────────────────
                'portfolio_page':     f'{base}portfolio/page/',
                'portfolio_categories': f'{base}portfolio/categories/',
                'portfolio_items':    f'{base}portfolio/items/',

                # ── Services ──────────────────────────────────
                'services':           f'{base}services/',
                'service_categories': f'{base}services/categories/',

                # ── Blog ──────────────────────────────────────
                'blog':               f'{base}blog/',
                'blog_categories':    f'{base}blog/categories/',

                # ── Contact & Enquiries ───────────────────────
                'contact':            f'{base}contact/',
                'contact_locations':  f'{base}contact-locations/',
                'enquiry':            f'{base}enquiry/',
                'careers':            f'{base}careers/',

                # ── Events ────────────────────────────────────
                'event_categories':   f'{base}event-categories/',
                'events':             f'{base}events/',

                # ── AI ────────────────────────────────────────
                'ai_generate_blog':   f'{base}ai/generate-blog/',
                'ai_logs':            f'{base}ai/logs/',

                # ── Chatbot ───────────────────────────────────
                'chat':               f'{base}chat/',
                'chat_sessions':      f'{base}chat/sessions/',

                # ── Docs & Health ─────────────────────────────
                'docs_swagger':       f'{base}docs/',
                'docs_redoc':         f'{base}docs/redoc/',
                'health':             f'{base}health/',
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
        return Response({
            'success':   True,
            'status':    'healthy',
            'database':  db,
            'timestamp': timezone.now().isoformat(),
        })