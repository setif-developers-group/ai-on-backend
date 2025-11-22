from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    MarkAsReadView,
    MarkAllAsReadView,
    UnreadCountView,
    DeleteNotificationView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/delete/', DeleteNotificationView.as_view(), name='notification-delete'),
    path('mark-all-read/', MarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),
]