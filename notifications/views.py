from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_inbox(request):
    """View to display all notifications for the authenticated stakeholder"""
    user_notifications = request.user.notifications.all()
    # Mark unread as seen when viewing the inbox (optional logic)
    # user_notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/inbox.html', {'notifications': user_notifications})

@login_required
def mark_as_read(request, pk):
    """Mark a specific notification node as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # If the notification has a link, redirect there, otherwise go back to inbox
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:inbox')

@login_required
def clear_all(request):
    """Remove all notifications for the user"""
    request.user.notifications.all().delete()
    return redirect('notifications:inbox')