"""
chat/views.py
POST /api/chat/                → send message, get reply
POST /api/chat/lead/           → save chatbot lead (name, phone, email, query)
GET  /api/chat/sessions/       → admin: list all sessions
GET  /api/chat/sessions/<key>/ → admin: view one session
"""
import logging
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework             import viewsets, status
from rest_framework.permissions import AllowAny, IsAdminUser

from .models      import ChatSession, ChatMessage, ChatLead
from .serializers import (
    MessageInputSerializer,
    ChatSessionSerializer,
    ChatLeadSerializer,
)
from .engine      import get_reply

logger = logging.getLogger('chat')


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


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

        return Response({
            'success'    : True,
            'message'    : reply,
            'session_key': session_key,
        })


# ── NEW: Lead capture (public — called by the chatbot widget) ────────────────
class ChatLeadView(APIView):
    """
    POST /api/chat/lead/
    Body: {
        "session_key": "<uuid>",       (optional)
        "name":        "John",
        "phone":       "9876543210",
        "email":       "john@x.com",
        "query":       "I need a quote"
    }
    Returns: { "success": true, "lead_id": 12, "message": "Lead saved." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ChatLeadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        lead = ser.save(ip_address=_client_ip(request))
        logger.info('New chatbot lead #%s from %s (%s)', lead.id, lead.name, lead.phone)

        return Response({
            'success': True,
            'lead_id': lead.id,
            'message': 'Lead saved successfully.',
        }, status=status.HTTP_201_CREATED)


class ChatLeadViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin only — view all chatbot leads via API.
    GET /api/chat/leads/
    GET /api/chat/leads/<id>/
    """
    serializer_class   = ChatLeadSerializer
    permission_classes = [IsAdminUser]
    queryset           = ChatLead.objects.all()


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
