from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification details.
    """
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'priority', 'title', 'message',
            'is_read', 'created_at', 'read_at', 'related_budget_id',
            'related_expense_id', 'action_url', 'action_data'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications (internal use by services).
    """
    class Meta:
        model = Notification
        fields = [
            'notification_type', 'priority', 'title', 'message',
            'related_budget_id', 'related_expense_id', 'action_url', 'action_data'
        ]


class NotificationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating notification read status.
    """
    is_read = serializers.BooleanField(required=True)


class UnreadCountSerializer(serializers.Serializer):
    """
    Serializer for unread count response.
    """
    unread_count = serializers.IntegerField()
