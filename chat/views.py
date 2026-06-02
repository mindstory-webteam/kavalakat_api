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

from .models      import ChatSession, ChatMessage
from .serializers import MessageInputSerializer, ChatSessionSerializer
from .engine      import get_reply

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

        return Response({
            'success'    : True,
            'message'    : reply,
            'session_key': session_key,
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
