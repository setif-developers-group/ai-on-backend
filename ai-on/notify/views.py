from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationUpdateSerializer,
    UnreadCountSerializer
)
from .services import mark_as_read, mark_all_as_read, get_unread_count


class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the authenticated user with optional filtering.
    
    Query Parameters:
    - read: Filter by read status (true/false)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='read',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by read status: "true" for read, "false" for unread, omit for all',
                required=False,
                enum=['true', 'false']
            )
        ],
        description="Get all notifications for the authenticated user. Use ?read=true/false to filter by read status."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status if provided
        read_param = self.request.query_params.get('read', None)
        if read_param is not None:
            if read_param.lower() == 'true':
                queryset = queryset.filter(is_read=True)
            elif read_param.lower() == 'false':
                queryset = queryset.filter(is_read=False)
        
        return queryset


class NotificationDetailView(APIView):
    """
    Get a specific notification and auto-mark it as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses=NotificationSerializer,
        description="Get notification details. Automatically marks the notification as read when viewed."
    )
    def get(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            
            # Auto-mark as read when viewed
            if not notification.is_read:
                notification.mark_as_read()
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkAsReadView(APIView):
    """
    Mark a specific notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses=NotificationSerializer,
        description="Mark a specific notification as read."
    )
    def patch(self, request, pk):
        success = mark_as_read(pk, request.user)
        
        if success:
            notification = Notification.objects.get(pk=pk, user=request.user)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkAllAsReadView(APIView):
    """
    Mark all notifications as read for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={'200': {'type': 'object', 'properties': {'marked_count': {'type': 'integer'}}}},
        description="Mark all unread notifications as read for the authenticated user."
    )
    def post(self, request):
        count = mark_all_as_read(request.user)
        return Response({"marked_count": count})


class UnreadCountView(APIView):
    """
    Get the count of unread notifications.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses=UnreadCountSerializer,
        description="Get the count of unread notifications for the authenticated user."
    )
    def get(self, request):
        count = get_unread_count(request.user)
        return Response({"unread_count": count})


class DeleteNotificationView(APIView):
    """
    Delete a specific notification.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={'204': None},
        description="Delete a specific notification."
    )
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )
