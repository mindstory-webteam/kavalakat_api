def dashboard_globals(request):
    if request.path.startswith('/dashboard/') and request.user.is_authenticated and request.user.is_staff:
        try:
            from contact.models import Enquiry
            count = Enquiry.objects.filter(status='new').count()
        except Exception:
            count = 0
        try:
            from chat.models import Lead
            pending_lead_count = Lead.objects.filter(status=Lead.STATUS_PENDING).count()
        except Exception:
            pending_lead_count = 0
        return {'new_enquiry_count': count, 'pending_lead_count': pending_lead_count}
    return {}
