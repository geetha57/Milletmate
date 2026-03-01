from .models import Notification

def notification_stats(request):
    """
    Makes unread notification count available globally across all templates.
    """
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count(),
            'has_unread_notifications': request.user.notifications.filter(is_read=False).exists()
        }
    return {
        'unread_notifications_count': 0,
        'has_unread_notifications': False
    }