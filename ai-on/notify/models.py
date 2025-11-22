from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """
    Centralized notification model for all user notifications.
    All agents can create notifications through the notify service.
    """
    NOTIFICATION_TYPES = [
        ('budget_alert', 'Budget Alert'),
        ('expense_alert', 'Expense Alert'),
        ('advisor_tip', 'Advisor Tip'),
        ('goal_milestone', 'Goal Milestone'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Link to related objects for deep linking
    related_budget_id = models.IntegerField(null=True, blank=True, help_text="ID of related budget")
    related_expense_id = models.IntegerField(null=True, blank=True, help_text="ID of related expense")
    
    # Optional: Action data for frontend interactivity
    action_url = models.CharField(max_length=255, null=True, blank=True, help_text="URL to navigate to on click")
    action_data = models.JSONField(null=True, blank=True, help_text="Additional data for frontend actions")
    
    class Meta:
        ordering = ['-created_at']  # Newest first
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"
    
    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
