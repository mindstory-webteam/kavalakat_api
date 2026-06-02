"""
chat/engine.py
──────────────────────────────────────────────────────────────────────────────
Smart rule-based chatbot engine.
NO external API needed — uses your own database.

Response priority:
  1. Admin-managed FAQs  (ChatbotFAQ model)
  2. Live Services data  (services.models)
  3. Contact info        (contact.models)
  4. About / company     (about.models)
  5. Careers / jobs      (contact.models Career)
  6. General greetings / fallback
"""

import re
import logging

logger = logging.getLogger('chat')


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase, strip punctuation for matching."""
    return re.sub(r'[^\w\s]', '', text.lower()).strip()


def _contains(text: str, *keywords) -> bool:
    """Check if any keyword appears in the text."""
    n = _normalise(text)
    return any(kw in n for kw in keywords)


# ─── DATA FETCHERS ────────────────────────────────────────────────────────────

def _get_services():
    try:
        from services.models import Service
        return list(
            Service.objects
            .select_related('category')
            .filter(is_active=True)
            .order_by('order', 'name')[:30]
        )
    except Exception as e:
        logger.warning('services fetch error: %s', e)
        return []


def _get_categories():
    try:
        from services.models import ServiceCategory
        return list(
            ServiceCategory.objects
            .filter(is_active=True)
            .order_by('order', 'name')
        )
    except Exception as e:
        logger.warning('categories fetch error: %s', e)
        return []


def _get_contact():
    try:
        from contact.models import Contact
        return Contact.objects.order_by('-updated_at').first()
    except Exception as e:
        logger.warning('contact fetch error: %s', e)
        return None


def _get_about():
    try:
        from about.models import About
        return About.objects.first()
    except Exception as e:
        logger.warning('about fetch error: %s', e)
        return None


def _get_careers():
    try:
        from contact.models import Career
        return list(
            Career.objects
            .filter(is_active=True)
            .order_by('-created_at')[:5]
        )
    except Exception as e:
        logger.warning('careers fetch error: %s', e)
        return []


def _get_faqs():
    try:
        from .models import ChatbotFAQ
        return list(ChatbotFAQ.objects.filter(is_active=True).order_by('order'))
    except Exception as e:
        logger.warning('faq fetch error: %s', e)
        return []


# ─── RESPONSE BUILDERS ────────────────────────────────────────────────────────

def _reply_services_list() -> str:
    services   = _get_services()
    categories = _get_categories()

    if not services:
        return (
            "We offer a wide range of professional services. "
            "Please contact our team for full details! 📞"
        )

    # Group by category
    grouped = {}
    for s in services:
        cat = s.category.name if s.category else 'General'
        grouped.setdefault(cat, []).append(s.name)

    lines = ["Here are our services:\n"]
    for cat, names in grouped.items():
        lines.append(f"**{cat}:**")
        for n in names:
            lines.append(f"  • {n}")

    lines.append("\nWould you like details about any specific service? 😊")
    return '\n'.join(lines)


def _reply_service_detail(text: str) -> str | None:
    """Return detail for a specific service if user mentions its name."""
    services = _get_services()
    text_lower = text.lower()

    for s in services:
        if s.name.lower() in text_lower:
            parts = [f"**{s.name}**"]
            if s.description:
                parts.append(s.description[:200])
            if s.category:
                parts.append(f"Category: {s.category.name}")

            # Add counters if available
            try:
                counters = s.counters.filter(is_active=True)[:3]
                if counters:
                    stats = ', '.join([f"{c.counter_number} {c.counter_title}" for c in counters])
                    parts.append(f"Key stats: {stats}")
            except Exception:
                pass

            parts.append("\nWant to know more? Feel free to contact our team! 👍")
            return '\n'.join(parts)
    return None


def _reply_contact() -> str:
    c = _get_contact()
    if not c:
        return "Please visit our website to get in touch with us! 😊"

    lines = ["Here's how to reach us:\n"]
    lines.append(f"📞 **Phone:** {c.phone}")
    if c.alt_phone:
        lines.append(f"📞 **Alt Phone:** {c.alt_phone}")
    lines.append(f"📧 **Email:** {c.email}")
    if c.whatsapp:
        lines.append(f"💬 **WhatsApp:** {c.whatsapp}")
    if c.address:
        addr = c.address
        if c.city:
            addr += f", {c.city}"
        lines.append(f"📍 **Address:** {addr}")
    if c.business_hours:
        lines.append(f"🕐 **Hours:** {c.business_hours}")
    lines.append("\nWe'd love to hear from you! 🤝")
    return '\n'.join(lines)


def _reply_about() -> str:
    about = _get_about()
    if not about:
        return (
            "Kavalakat is a leading professional services company based in Kerala, India. "
            "We provide high-quality services across multiple sectors. "
            "Contact us to learn more! 🏢"
        )

    lines = [f"**{about.title}**\n"]
    if about.description:
        lines.append(about.description[:300])
    if about.mission:
        lines.append(f"\n🎯 **Mission:** {about.mission[:150]}")
    if about.vision:
        lines.append(f"\n👁️ **Vision:** {about.vision[:150]}")
    return '\n'.join(lines)


def _reply_careers() -> str:
    careers = _get_careers()
    if not careers:
        return (
            "We don't have any open positions right now, but we're always "
            "looking for talented people! Send your resume to our email. 📩"
        )

    lines = ["We're hiring! Current openings:\n"]
    for job in careers:
        line = f"• **{job.title}**"
        if job.job_type:
            line += f" ({job.job_type})"
        if job.location:
            line += f" — {job.location}"
        lines.append(line)

    lines.append("\nInterested? Contact us or visit the Careers section of our website! 🚀")
    return '\n'.join(lines)


def _reply_featured_services() -> str:
    try:
        from services.models import Service
        featured = list(
            Service.objects
            .filter(is_active=True, is_featured=True)
            .order_by('order', 'name')[:6]
        )
        if featured:
            names = ', '.join([s.name for s in featured])
            return (
                f"Our featured services are: ⭐ {names}.\n\n"
                "Would you like details about any of these?"
            )
    except Exception:
        pass
    return _reply_services_list()


def _reply_location() -> str:
    c = _get_contact()
    if c and c.address:
        addr = c.address
        if c.city:
            addr += f", {c.city}"
        return (
            f"We are located at:\n📍 **{addr}**\n\n"
            "Feel free to visit us or contact us for directions! 🗺️"
        )
    return "We are based in Kerala, India. Contact us for our exact location! 📍"


# ─── FAQ MATCHER ──────────────────────────────────────────────────────────────

def _check_faqs(text: str) -> str | None:
    """Check admin-managed FAQs first."""
    faqs = _get_faqs()
    text_lower = _normalise(text)

    for faq in faqs:
        keywords = faq.keyword_list()
        if keywords:
            if any(kw in text_lower for kw in keywords):
                return faq.answer
        else:
            # No keywords — match question directly
            if _normalise(faq.question) in text_lower:
                return faq.answer
    return None


# ─── MAIN ENGINE ──────────────────────────────────────────────────────────────

def get_reply(user_message: str, history: list[dict] | None = None) -> str:
    """
    Main chatbot engine.
    Returns a reply string based on user_message.
    history = [{"role": "user"|"assistant", "content": "..."}]
    """
    text = user_message.strip()
    if not text:
        return "Please type a message and I'll be happy to help! 😊"

    # ── 1. Check admin FAQs first ────────────────────────────────────────────
    faq_reply = _check_faqs(text)
    if faq_reply:
        return faq_reply

    # ── 2. Greeting ──────────────────────────────────────────────────────────
    if _contains(text, 'hi', 'hello', 'hey', 'hlo', 'helo', 'good morning',
                 'good afternoon', 'good evening', 'howdy', 'namaste', 'hai'):
        c = _get_contact()
        name = 'Kavalakat'
        return (
            f"Hello! 👋 Welcome to {name}. I'm here to help you.\n\n"
            "You can ask me about:\n"
            "• Our services\n"
            "• Contact information\n"
            "• Job openings\n"
            "• About our company\n\n"
            "How can I assist you today? 😊"
        )

    # ── 3. Specific service detail ────────────────────────────────────────────
    detail = _reply_service_detail(text)
    if detail:
        return detail

    # ── 4. Services list ──────────────────────────────────────────────────────
    if _contains(text, 'service', 'services', 'what do you', 'what you offer',
                 'offer', 'provide', 'list', 'all service', 'show service'):
        return _reply_services_list()

    # ── 5. Featured services ──────────────────────────────────────────────────
    if _contains(text, 'featured', 'popular', 'best', 'top service',
                 'recommend', 'speciality', 'specialty'):
        return _reply_featured_services()

    # ── 6. Contact ────────────────────────────────────────────────────────────
    if _contains(text, 'contact', 'phone', 'call', 'email', 'mail',
                 'reach', 'whatsapp', 'number', 'touch', 'get in touch'):
        return _reply_contact()

    # ── 7. Location / address ─────────────────────────────────────────────────
    if _contains(text, 'location', 'address', 'where', 'office', 'place',
                 'visit', 'direction', 'map', 'area', 'situated'):
        return _reply_location()

    # ── 8. About company ─────────────────────────────────────────────────────
    if _contains(text, 'about', 'company', 'who are you', 'tell me about',
                 'kavalakat', 'organization', 'business', 'firm', 'mission',
                 'vision', 'history', 'founded', 'established'):
        return _reply_about()

    # ── 9. Careers / jobs ────────────────────────────────────────────────────
    if _contains(text, 'job', 'career', 'hiring', 'vacancy', 'opening',
                 'position', 'work', 'employment', 'apply', 'resume', 'cv'):
        return _reply_careers()

    # ── 10. Pricing ───────────────────────────────────────────────────────────
    if _contains(text, 'price', 'cost', 'rate', 'charge', 'fee', 'how much',
                 'pricing', 'quote', 'estimate', 'budget', 'cheap', 'affordable'):
        c = _get_contact()
        phone = c.phone if c else 'our team'
        return (
            "Our pricing varies based on your specific requirements. 💰\n\n"
            f"For an accurate quote, please contact us at **{phone}** "
            "or send us an email — we'll be happy to provide a customised estimate! 📧"
        )

    # ── 11. Thank you ─────────────────────────────────────────────────────────
    if _contains(text, 'thank', 'thanks', 'thank you', 'thx', 'ty',
                 'appreciated', 'great', 'awesome', 'perfect', 'wonderful'):
        return (
            "You're welcome! 😊 Is there anything else I can help you with?\n\n"
            "Feel free to ask about our services, contact details, or anything else!"
        )

    # ── 12. Bye / goodbye ────────────────────────────────────────────────────
    if _contains(text, 'bye', 'goodbye', 'see you', 'later', 'ok bye',
                 'take care', 'good night', 'cya'):
        return (
            "Thank you for reaching out! 👋\n\n"
            "Have a great day. Feel free to come back anytime — we're always here to help! 😊"
        )

    # ── 13. Help ─────────────────────────────────────────────────────────────
    if _contains(text, 'help', 'support', 'assist', 'guide', 'info',
                 'information', 'know', 'tell me'):
        return (
            "I'm here to help! 🤝 Here's what I can assist you with:\n\n"
            "• **Services** — Ask 'What services do you offer?'\n"
            "• **Contact** — Ask 'How can I contact you?'\n"
            "• **Location** — Ask 'Where are you located?'\n"
            "• **About** — Ask 'Tell me about Kavalakat'\n"
            "• **Jobs** — Ask 'Are you hiring?'\n"
            "• **Pricing** — Ask 'What are your rates?'\n\n"
            "What would you like to know? 😊"
        )

    # ── 14. Fallback ─────────────────────────────────────────────────────────
    c       = _get_contact()
    phone   = c.phone if c else ''
    email   = c.email if c else ''
    contact = f" Call us at {phone} or email {email}." if (phone or email) else ""

    return (
        "I'm not sure I understood that. 🤔 Let me connect you with our team!\n\n"
        f"{contact}\n\n"
        "Or you can ask me about:\n"
        "• Our **services**\n"
        "• **Contact** details\n"
        "• **Job** openings\n"
        "• **About** us"
    )
