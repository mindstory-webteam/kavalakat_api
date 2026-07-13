"""
chat/engine.py
──────────────────────────────────────────────────────────────────────────────
Enhanced chatbot engine — covers:
  1. Admin FAQs
  2. Services + categories
  3. Portfolio items + categories + details
  4. Contact info
  5. About / company / mission / vision / strengths
  6. Careers / jobs
  7. General greetings, pricing, location, help, bye
"""

import re
import json
import logging

logger = logging.getLogger('chat')


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text.lower()).strip()

def _has(text: str, *keywords) -> bool:
    n = _norm(text)
    return any(kw in n for kw in keywords)


# ─── DATA FETCHERS ────────────────────────────────────────────────────────────

def _services():
    try:
        from services.models import Service
        return list(Service.objects.select_related('category').filter(is_active=True).order_by('order', 'name')[:40])
    except Exception as e:
        logger.warning('services: %s', e); return []

def _service_categories():
    try:
        from services.models import ServiceCategory
        return list(ServiceCategory.objects.filter(is_active=True).order_by('order', 'name'))
    except Exception as e:
        logger.warning('service_cats: %s', e); return []

def _portfolio_items():
    try:
        from portfolio.models import Item
        return list(Item.objects.select_related('category').filter(is_active=True).order_by('order', 'name')[:50])
    except Exception as e:
        logger.warning('portfolio_items: %s', e); return []

def _portfolio_categories():
    try:
        from portfolio.models import Category
        return list(Category.objects.filter(is_active=True).order_by('order', 'name'))
    except Exception as e:
        logger.warning('portfolio_cats: %s', e); return []

def _contact():
    try:
        from contact.models import Contact
        return Contact.objects.order_by('-updated_at').first()
    except Exception as e:
        logger.warning('contact: %s', e); return None

def _about():
    try:
        from about.models import About
        return About.objects.first()
    except Exception as e:
        logger.warning('about: %s', e); return None

def _strengths():
    try:
        from about.models import Strength
        return list(Strength.objects.filter(is_active=True).order_by('order')[:6])
    except Exception as e:
        logger.warning('strengths: %s', e); return []

def _milestones():
    try:
        from about.models import Milestone
        return list(Milestone.objects.order_by('-year')[:5])
    except Exception as e:
        logger.warning('milestones: %s', e); return []

def _careers():
    try:
        from contact.models import Career
        return list(Career.objects.filter(is_active=True).order_by('-created_at')[:5])
    except Exception as e:
        logger.warning('careers: %s', e); return []

def _faqs():
    try:
        from .models import ChatbotFAQ
        return list(ChatbotFAQ.objects.filter(is_active=True).order_by('order'))
    except Exception as e:
        logger.warning('faqs: %s', e); return []


# ─── RESPONSE BUILDERS ────────────────────────────────────────────────────────

def _r_services_list() -> str:
    services = _services()
    if not services:
        return "We offer a wide range of professional services. Contact us for full details! 📞"
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


def _r_service_detail(text: str):
    for s in _services():
        if s.name.lower() in text.lower():
            parts = [f"**{s.name}**"]
            if s.description:
                parts.append(s.description[:200])
            if s.category:
                parts.append(f"Category: {s.category.name}")
            try:
                counters = s.counters.filter(is_active=True)[:3]
                if counters:
                    stats = ', '.join([f"{c.counter_number} {c.counter_title}" for c in counters])
                    parts.append(f"Key stats: {stats}")
            except Exception:
                pass
            parts.append("\nFor more details, feel free to contact our team! 👍")
            return '\n'.join(parts)
    return None


def _r_portfolio_list() -> str:
    items = _portfolio_items()
    cats  = _portfolio_categories()
    if not items:
        return "We have an extensive portfolio of projects. Contact us to learn more! 🏗️"

    grouped = {}
    for item in items:
        cat = item.category.name if item.category else 'General'
        grouped.setdefault(cat, []).append(item.name)

    lines = ["Here's our portfolio:\n"]
    for cat, names in grouped.items():
        lines.append(f"**{cat}:**")
        for n in names[:5]:
            lines.append(f"  • {n}")
        if len(names) > 5:
            lines.append(f"  • ...and {len(names)-5} more")

    lines.append("\nAsk me about any specific project for more details! 😊")
    return '\n'.join(lines)


def _r_portfolio_categories() -> str:
    cats = _portfolio_categories()
    if not cats:
        return "We work across multiple sectors. Ask me about our portfolio for details!"
    lines = ["Our portfolio categories:\n"]
    for cat in cats:
        count = cat.items.filter(is_active=True).count() if hasattr(cat, 'items') else 0
        line  = f"  • **{cat.name}**"
        if count:
            line += f" ({count} projects)"
        if cat.description:
            line += f" — {cat.description[:80]}"
        lines.append(line)
    lines.append("\nWould you like to see projects in a specific category? 🏗️")
    return '\n'.join(lines)


def _r_portfolio_detail(text: str):
    """Return detail for a specific portfolio item."""
    text_lower = text.lower()
    items = _portfolio_items()

    # Match by item name
    for item in items:
        if item.name.lower() in text_lower:
            parts = [f"**{item.name}**"]
            if item.category:
                parts.append(f"Category: {item.category.name}")
            if item.description:
                parts.append(f"\n{item.description[:250]}")
            if item.hero_title:
                parts.append(f"\n{item.hero_title}")
            if item.about_title:
                parts.append(f"\n**About:** {item.about_title}")
            if item.about_description:
                parts.append(item.about_description[:200])

            # Features
            try:
                features = item.get_features()
                if features:
                    parts.append("\n**Key Features:**")
                    for f in features[:4]:
                        parts.append(f"  • {f.get('title','')}: {f.get('description','')[:80]}")
            except Exception:
                pass

            # Brands/locations
            try:
                brands = item.get_brands()
                if brands:
                    brand_names = [b.get('title','') for b in brands[:5] if b.get('title')]
                    if brand_names:
                        parts.append(f"\n**Locations/Brands:** {', '.join(brand_names)}")
            except Exception:
                pass

            parts.append("\nContact us for more information or a quote! 📞")
            return '\n'.join(parts)

    # Match by category name
    cats = _portfolio_categories()
    for cat in cats:
        if cat.name.lower() in text_lower:
            cat_items = [i for i in items if i.category_id == cat.id]
            if cat_items:
                lines = [f"**{cat.name}** projects:\n"]
                for i in cat_items[:8]:
                    lines.append(f"  • {i.name}")
                lines.append(f"\nWe have {len(cat_items)} projects in {cat.name}. Ask about any specific one!")
                return '\n'.join(lines)

    return None


def _r_featured_portfolio() -> str:
    try:
        from portfolio.models import Item
        featured = list(Item.objects.filter(is_active=True, is_featured=True).order_by('order')[:6])
        if featured:
            names = ', '.join([i.name for i in featured])
            return f"Our featured portfolio projects: ⭐ {names}\n\nAsk me about any of these for details!"
    except Exception:
        pass
    return _r_portfolio_list()


def _r_contact() -> str:
    c = _contact()
    if not c:
        return "Please visit our website to get in touch! 😊"
    lines = ["Here's how to reach us:\n"]
    lines.append(f"📞 **Phone:** {c.phone}")
    if getattr(c, 'alt_phone', None):
        lines.append(f"📞 **Alt Phone:** {c.alt_phone}")
    lines.append(f"📧 **Email:** {c.email}")
    if getattr(c, 'whatsapp', None):
        lines.append(f"💬 **WhatsApp:** {c.whatsapp}")
    if getattr(c, 'address', None):
        addr = c.address
        if getattr(c, 'city', None): addr += f", {c.city}"
        lines.append(f"📍 **Address:** {addr}")
    if getattr(c, 'business_hours', None):
        lines.append(f"🕐 **Hours:** {c.business_hours}")
    lines.append("\nWe'd love to hear from you! 🤝")
    return '\n'.join(lines)


def _r_about() -> str:
    about = _about()
    if not about:
        return "Kavalakat is a leading professional services company based in Kerala, India. 🏢"
    lines = [f"**{about.title}**\n"]
    if about.description:
        lines.append(about.description[:300])
    if about.mission:
        lines.append(f"\n🎯 **Mission:** {about.mission[:150]}")
    if about.vision:
        lines.append(f"\n👁️ **Vision:** {about.vision[:150]}")
    return '\n'.join(lines)


def _r_strengths() -> str:
    strengths = _strengths()
    if not strengths:
        return _r_about()
    lines = ["**Our Key Strengths:**\n"]
    for s in strengths:
        line = f"  • **{s.title}**"
        if s.description:
            line += f" — {s.description[:80]}"
        lines.append(line)
    return '\n'.join(lines)


def _r_careers() -> str:
    careers = _careers()
    if not careers:
        return "No open positions right now, but we're always looking for talented people! Send your CV to our email. 📩"
    lines = ["We're hiring! Current openings:\n"]
    for job in careers:
        line = f"• **{job.title}**"
        if getattr(job, 'job_type', None): line += f" ({job.job_type})"
        if getattr(job, 'location', None): line += f" — {job.location}"
        lines.append(line)
    lines.append("\nContact us or visit the Careers section to apply! 🚀")
    return '\n'.join(lines)


def _r_location() -> str:
    c = _contact()
    if c and getattr(c, 'address', None):
        addr = c.address
        if getattr(c, 'city', None): addr += f", {c.city}"
        return f"We are located at:\n📍 **{addr}**\n\nFeel free to visit us or contact us for directions! 🗺️"
    return "We are based in Kerala, India. Contact us for our exact location! 📍"


def _r_featured_services() -> str:
    try:
        from services.models import Service
        featured = list(Service.objects.filter(is_active=True, is_featured=True).order_by('order')[:6])
        if featured:
            names = ', '.join([s.name for s in featured])
            return f"Our featured services: ⭐ {names}\n\nWould you like details about any of these?"
    except Exception:
        pass
    return _r_services_list()


# ─── FAQ MATCHER ──────────────────────────────────────────────────────────────

def _check_faqs(text: str):
    text_lower = _norm(text)
    for faq in _faqs():
        keywords = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
        if keywords:
            if any(kw in text_lower for kw in keywords):
                return faq.answer
        else:
            if _norm(faq.question) in text_lower:
                return faq.answer
    return None


# ─── MAIN ENGINE ──────────────────────────────────────────────────────────────

def get_reply(user_message: str, history: list | None = None) -> str:
    text = user_message.strip()
    if not text:
        return "Please type a message and I'll be happy to help! 😊"

    # ── 1. Admin FAQs ────────────────────────────────────────────────────────
    faq = _check_faqs(text)
    if faq:
        return faq

    # ── 2. Greeting ──────────────────────────────────────────────────────────
    if _has(text, 'hi', 'hello', 'hey', 'hlo', 'helo', 'good morning',
            'good afternoon', 'good evening', 'howdy', 'namaste', 'hai',
            'helloo', 'hellooo', 'heloo'):
        return (
            "Hello! 👋 Welcome to Kavalakat. I'm here to help you.\n\n"
            "You can ask me about:\n"
            "• Our **services**\n"
            "• Our **portfolio** & projects\n"
            "• **Contact** information\n"
            "• **Job** openings\n"
            "• **About** our company\n\n"
            "How can I assist you today? 😊"
        )

    # ── 3. Portfolio category detail ─────────────────────────────────────────
    if _has(text, 'portfolio', 'project', 'work', 'client', 'case study'):
        # Check for specific item/category first
        detail = _r_portfolio_detail(text)
        if detail:
            return detail
        # Featured portfolio
        if _has(text, 'featured', 'best', 'top', 'highlight'):
            return _r_featured_portfolio()
        # Categories
        if _has(text, 'categor', 'sector', 'type', 'division'):
            return _r_portfolio_categories()
        # General portfolio list
        return _r_portfolio_list()

    # ── 4. Specific portfolio item by name ───────────────────────────────────
    port_detail = _r_portfolio_detail(text)
    if port_detail:
        return port_detail

    # ── 5. Specific service detail ───────────────────────────────────────────
    svc_detail = _r_service_detail(text)
    if svc_detail:
        return svc_detail

    # ── 6. Services ──────────────────────────────────────────────────────────
    if _has(text, 'service', 'services', 'what do you', 'what you offer',
            'offer', 'provide', 'list service', 'all service', 'show service',
            'what can you', 'solutions'):
        return _r_services_list()

    # ── 7. Featured services ─────────────────────────────────────────────────
    if _has(text, 'featured', 'popular', 'best service', 'top service',
            'speciality', 'specialty', 'recommend'):
        return _r_featured_services()

    # ── 8. Contact ───────────────────────────────────────────────────────────
    if _has(text, 'contact', 'phone', 'call', 'email', 'mail',
            'reach', 'whatsapp', 'number', 'touch', 'get in touch',
            'enquiry', 'inquiry', 'quote', 'estimate'):
        return _r_contact()

    # ── 9. Location ──────────────────────────────────────────────────────────
    if _has(text, 'location', 'address', 'where', 'office', 'place',
            'visit', 'direction', 'map', 'area', 'situated', 'based',
            'headquarter', 'kerala'):
        return _r_location()

    # ── 10. About / company ──────────────────────────────────────────────────
    if _has(text, 'about', 'company', 'who are you', 'tell me about',
            'kavalakat', 'organization', 'business', 'firm', 'history',
            'founded', 'established', 'background'):
        return _r_about()

    # ── 11. Mission / vision ─────────────────────────────────────────────────
    if _has(text, 'mission', 'vision', 'goal', 'objective', 'purpose', 'value'):
        return _r_about()

    # ── 12. Strengths / why us ───────────────────────────────────────────────
    if _has(text, 'strength', 'why choose', 'why us', 'advantage',
            'benefit', 'unique', 'experience', 'expertise', 'quality'):
        return _r_strengths()

    # ── 13. Careers / jobs ───────────────────────────────────────────────────
    if _has(text, 'job', 'career', 'hiring', 'vacancy', 'opening',
            'position', 'employment', 'apply', 'resume', 'cv', 'work with'):
        return _r_careers()

    # ── 14. Pricing ──────────────────────────────────────────────────────────
    if _has(text, 'price', 'cost', 'rate', 'charge', 'fee', 'how much',
            'pricing', 'budget', 'cheap', 'affordable', 'expensive'):
        c     = _contact()
        phone = c.phone if c else 'our team'
        return (
            "Our pricing varies based on your specific requirements. 💰\n\n"
            f"Please contact us at **{phone}** or send an email for a customised quote!\n"
            "We ensure competitive pricing with the best quality. 🤝"
        )

    # ── 15. Trading specific ─────────────────────────────────────────────────
    if _has(text, 'trading', 'trade', 'commodity', 'steel', 'cement',
            'material', 'supply', 'supplier'):
        detail = _r_portfolio_detail(text)
        if detail:
            return detail
        return _r_portfolio_categories()

    # ── 16. Distribution specific ────────────────────────────────────────────
    if _has(text, 'distribut', 'dealer', 'wholesale', 'retail', 'stock'):
        detail = _r_portfolio_detail(text)
        if detail:
            return detail
        return _r_portfolio_categories()

    # ── 17. Thank you ────────────────────────────────────────────────────────
    if _has(text, 'thank', 'thanks', 'thank you', 'thx', 'ty',
            'great', 'awesome', 'perfect', 'wonderful', 'excellent', 'good'):
        return "You're welcome! 😊 Is there anything else I can help you with?"

    # ── 18. Bye ──────────────────────────────────────────────────────────────
    if _has(text, 'bye', 'goodbye', 'see you', 'later', 'ok bye', 'take care'):
        return "Thank you for reaching out! 👋 Have a great day. Feel free to come back anytime! 😊"

    # ── 19. Help ─────────────────────────────────────────────────────────────
    if _has(text, 'help', 'support', 'assist', 'guide', 'info', 'information'):
        return (
            "I'm here to help! 🤝 Here's what I can assist with:\n\n"
            "• **Services** — 'What services do you offer?'\n"
            "• **Portfolio** — 'Show me your portfolio'\n"
            "• **Projects** — 'Tell me about Trading projects'\n"
            "• **Contact** — 'How can I contact you?'\n"
            "• **Location** — 'Where are you located?'\n"
            "• **About** — 'Tell me about Kavalakat'\n"
            "• **Jobs** — 'Are you hiring?'\n"
            "• **Pricing** — 'What are your rates?'\n\n"
            "What would you like to know? 😊"
        )

    # ── 20. Fallback ─────────────────────────────────────────────────────────
    c     = _contact()
    phone = c.phone if c else ''
    email = c.email if c else ''

    return (
        "I'm not sure I understood that. 🤔\n\n"
        f"{'📞 Call us: ' + phone if phone else ''}"
        f"{'  |  📧 ' + email if email else ''}\n\n"
        "Or ask me about:\n"
        "• Our **services** or **portfolio**\n"
        "• **Contact** details\n"
        "• **Job** openings\n"
        "• **About** us"
    )