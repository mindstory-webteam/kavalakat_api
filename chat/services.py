"""
chat/services.py
Handles the Anthropic Claude API call and builds the dynamic system prompt
from live Kavalakat database content (services, categories, contact info).
"""
import logging
from django.conf import settings

logger = logging.getLogger('chat')


# ─── SYSTEM PROMPT BUILDER ────────────────────────────────────────────────────

def build_system_prompt() -> str:
    """
    Pulls live data from the DB so Claude always has up-to-date
    service / contact info when answering users.
    """
    # ── Services ────────────────────────────────────────────────────────────
    service_lines = []
    try:
        from services.models import Service, ServiceCategory
        services = (
            Service.objects
            .select_related('category')
            .filter(is_active=True)
            .order_by('order', 'name')[:40]
        )
        for s in services:
            cat   = s.category.name if s.category else 'General'
            feat  = ' ⭐' if s.is_featured else ''
            desc  = s.description[:120] if s.description else ''
            service_lines.append(f'  • {s.name} [{cat}]{feat} — {desc}')

        categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
        cat_lines  = [f'  • {c.name}: {c.description[:80]}' for c in categories]
    except Exception as exc:
        logger.warning('Could not load services: %s', exc)
        service_lines = ['  (services unavailable)']
        cat_lines     = []

    # ── Contact info ─────────────────────────────────────────────────────────
    contact_block = ''
    try:
        from contact.models import Contact
        c = Contact.objects.order_by('-updated_at').first()
        if c:
            contact_block = f"""
## Contact Information
- Phone: {c.phone}{(' / ' + c.alt_phone) if c.alt_phone else ''}
- Email: {c.email}{(' / ' + c.alt_email) if c.alt_email else ''}
- WhatsApp: {c.whatsapp or c.phone}
- Address: {c.address}{(', ' + c.city) if c.city else ''}{(', ' + c.state) if c.state else ''}
{('- Business Hours: ' + c.business_hours) if c.business_hours else ''}"""
    except Exception as exc:
        logger.warning('Could not load contact: %s', exc)
        contact_block = '## Contact\nPlease visit our website for contact details.'

    services_block   = '\n'.join(service_lines) or '  (no services found)'
    categories_block = '\n'.join(cat_lines)     or '  (no categories)'

    return f"""You are a friendly and professional AI Assistant for Kavalakat, \
a leading services company based in Kerala, India.

## Your Role
- Answer questions about Kavalakat's services, locations, pricing enquiries, and team
- Guide visitors toward the right service for their needs
- Encourage users to contact the team for detailed quotes or bookings
- Be warm, concise, and helpful — like a knowledgeable customer support agent

## Available Services
{services_block}

## Service Categories
{categories_block}
{contact_block}

## Guidelines
- Keep replies under 120 words unless listing multiple services
- Use bullet points only when listing 3+ items
- Never invent pricing — always say "contact our team for a quote"
- If unsure, offer to connect the user with the team directly
- Be polite and professional at all times
- You can use 1–2 emojis per message for warmth, but don't overdo it
- Company website: https://tan-rail-168119.hostingersite.com
- API / backend: https://api.kavalakat.com
"""


# ─── CLAUDE API CALL ─────────────────────────────────────────────────────────

def chat_with_claude(messages: list[dict]) -> str:
    """
    messages = [{"role": "user"|"assistant", "content": "..."}]
    Returns the assistant reply as a plain string.
    Raises RuntimeError on API / config failure.
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '').strip()
    if not api_key:
        raise ValueError('ANTHROPIC_API_KEY is not configured in settings / .env')

    try:
        import anthropic
    except ImportError:
        raise ValueError('anthropic package not installed. Run: pip install anthropic')

    client = anthropic.Anthropic(api_key=api_key)

    # Keep last 10 turns to stay within context limits
    history = messages[-10:]

    try:
        response = client.messages.create(
            model   = 'claude-sonnet-4-20250514',
            max_tokens = 600,
            system  = build_system_prompt(),
            messages = history,
        )
    except Exception as exc:
        logger.error('Anthropic API error: %s', exc)
        raise RuntimeError(f'AI service error: {exc}') from exc

    return response.content[0].text.strip()
