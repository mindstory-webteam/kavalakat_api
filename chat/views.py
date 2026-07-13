"""
chat/views.py
POST /api/chat/              → send message, get reply
GET  /api/chat/sessions/     → admin: list all sessions
GET  /api/chat/sessions/<key>/ → admin: view one session
"""
import logging
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework             import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser

from .models      import ChatSession, ChatMessage, Lead
from .serializers import (
    MessageInputSerializer, ChatSessionSerializer,
    LeadCreateSerializer, LeadSerializer,
)
from .engine      import get_reply, wants_lead_capture

logger = logging.getLogger('chat')


class ChatView(APIView):
    """
    POST /api/chat/
    Body:    { "session_key": "<uuid>", "message": "hello" }
    Returns: { "success": true, "message": "<reply>", "session_key": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        inp = MessageInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)

        session_key = inp.validated_data['session_key']
        user_text   = inp.validated_data['message']

        # Get or create session
        session, _ = ChatSession.objects.get_or_create(session_key=session_key)

        # Save user message
        ChatMessage.objects.create(
            session = session,
            role    = ChatMessage.ROLE_USER,
            content = user_text,
        )

        # Build history (last 10 turns for context)
        history = list(
            session.messages
            .order_by('created_at')
            .values('role', 'content')
        )[-10:]

        # Get reply from engine (no external API)
        try:
            reply = get_reply(user_text, history=history)
        except Exception as exc:
            logger.error('Chat engine error for session %s: %s', session_key, exc)
            reply = (
                "Sorry, I had a small hiccup! 😔 "
                "Please try again or contact us directly."
            )

        # Save assistant reply
        ChatMessage.objects.create(
            session = session,
            role    = ChatMessage.ROLE_ASSISTANT,
            content = reply,
        )

        session.save(update_fields=['updated_at'])

        # Already captured a lead for this session? Don't ask again.
        already_has_lead = session.leads.exists()
        capture_lead = (not already_has_lead) and wants_lead_capture(user_text, reply)

        return Response({
            'success'     : True,
            'message'     : reply,
            'session_key' : session_key,
            'capture_lead': capture_lead,
        })


class LeadCreateView(APIView):
    """
    POST /api/chat/leads/
    Body:    { "session_key": "...", "name": "...", "phone": "...",
                "email": "...", "query": "..." }
    Returns: { "success": true, "message": "..." }

    Used by the public chatbot widget's lead-capture form. Anyone can
    submit — no auth required — same as the chat endpoint itself.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        inp = LeadCreateSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        data = inp.validated_data

        session = None
        session_key = data.get('session_key', '').strip()
        if session_key:
            session, _ = ChatSession.objects.get_or_create(session_key=session_key)

        lead = Lead.objects.create(
            session = session,
            name    = data['name'],
            phone   = data.get('phone', ''),
            email   = data.get('email', ''),
            query   = data.get('query', '').strip() or 'General enquiry from chatbot',
        )

        logger.info('New chatbot lead captured: %s (id=%s)', lead.name, lead.id)

        return Response({
            'success': True,
            'message': "Thanks! We've received your details and our team will reach out shortly. 🙌",
            'lead_id': lead.id,
        }, status=status.HTTP_201_CREATED)


class LeadViewSet(viewsets.ModelViewSet):
    """
    Admin only — manage chatbot leads.
    GET    /api/chat/leads/manage/           list
    GET    /api/chat/leads/manage/<pk>/      retrieve
    PATCH  /api/chat/leads/manage/<pk>/      update status
    DELETE /api/chat/leads/manage/<pk>/      delete
    """
    serializer_class   = LeadSerializer
    permission_classes = [IsAdminUser]
    queryset            = Lead.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        qs     = self.filter_queryset(self.get_queryset())
        status_q = request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response({
            'success': True,
            'count'  : qs.count(),
            'data'   : self.get_serializer(qs, many=True).data,
        })


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin only — view all sessions and messages.
    GET /api/chat/sessions/
    GET /api/chat/sessions/<session_key>/
    """
    serializer_class   = ChatSessionSerializer
    permission_classes = [IsAdminUser]
    lookup_field       = 'session_key'

    def get_queryset(self):
        return (
            ChatSession.objects
            .prefetch_related('messages')
            .order_by('-updated_at')
        )

    def list(self, request, *args, **kwargs):
        qs   = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response({
            'success': True,
            'count'  : qs.count(),
            'data'   : self.get_serializer(qs, many=True).data,
        })

    def retrieve(self, request, *args, **kwargs):
        return Response({
            'success': True,
            'data'   : self.get_serializer(self.get_object()).data,
        })
