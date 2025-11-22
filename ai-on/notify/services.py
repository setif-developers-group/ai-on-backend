"""
Notify Service

Centralized notification service that all agents can use to create and manage notifications.
"""

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Notification


def create_notification(
    user: User,
    notification_type: str,
    title: str,
    message: str,
    priority: str = 'medium',
    related_budget_id: int = None,
    related_expense_id: int = None,
    action_url: str = None,
    action_data: dict = None
) -> Notification:
    """
    Create a new notification for a user.
    
    This is the main function that all agents should call to create notifications.
    
    Args:
        user: The Django User object
        notification_type: Type of notification ('budget_alert', 'expense_alert', etc.)
        title: Notification title
        message: Notification message
        priority: Priority level ('low', 'medium', 'high', 'urgent')
        related_budget_id: Optional ID of related budget
        related_expense_id: Optional ID of related expense
        action_url: Optional URL for frontend navigation
        action_data: Optional JSON data for frontend actions
        
    Returns:
        Created Notification object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        priority=priority,
        title=title,
        message=message,
        related_budget_id=related_budget_id,
        related_expense_id=related_expense_id,
        action_url=action_url,
        action_data=action_data
    )
    
    print(f"DEBUG: Created notification for {user.username}: {title}")
    return notification


def mark_as_read(notification_id: int, user: User) -> bool:
    """
    Mark a specific notification as read.
    
    Args:
        notification_id: ID of the notification
        user: The Django User object (for security check)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.mark_as_read()
        return True
    except Notification.DoesNotExist:
        return False


def mark_all_as_read(user: User) -> int:
    """
    Mark all unread notifications as read for a user.
    
    Args:
        user: The Django User object
        
    Returns:
        Number of notifications marked as read
    """
    unread_notifications = Notification.objects.filter(user=user, is_read=False)
    count = unread_notifications.count()
    
    # Update all at once
    unread_notifications.update(is_read=True, read_at=timezone.now())
    
    print(f"DEBUG: Marked {count} notifications as read for {user.username}")
    return count


def get_unread_count(user: User) -> int:
    """
    Get the count of unread notifications for a user.
    
    Args:
        user: The Django User object
        
    Returns:
        Count of unread notifications
    """
    return Notification.objects.filter(user=user, is_read=False).count()


def delete_old_notifications(days: int = 30) -> int:
    """
    Delete notifications older than specified days.
    
    This can be run as a periodic cleanup task.
    
    Args:
        days: Number of days to keep notifications
        
    Returns:
        Number of notifications deleted
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    old_notifications = Notification.objects.filter(created_at__lt=cutoff_date)
    count = old_notifications.count()
    old_notifications.delete()
    
    print(f"DEBUG: Deleted {count} notifications older than {days} days")
    return count


def get_notifications(user: User, is_read: bool = None, limit: int = None):
    """
    Get notifications for a user with optional filtering.
    
    Args:
        user: The Django User object
        is_read: Optional filter for read status (True/False/None for all)
        limit: Optional limit on number of notifications
        
    Returns:
        QuerySet of Notification objects
    """
    notifications = Notification.objects.filter(user=user)
    
    if is_read is not None:
        notifications = notifications.filter(is_read=is_read)
    
    if limit:
        notifications = notifications[:limit]
    
    return notifications
