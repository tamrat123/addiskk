import datetime
from .models import Notification

def notification_processor(request):
    today = datetime.date.today()
    if request.user.is_authenticated:
        qs = Notification.objects.filter(is_read=False)
        if request.user.role != 'HQ_ADMIN' and hasattr(request.user, 'branch'):
            qs = qs.filter(branch=request.user.branch)
        return {
            'notifications': qs.order_by('-created_at')[:5],
            'today': today
        }
    return {'notifications': [], 'today': today}
