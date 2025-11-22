from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'notification_type', 'priority', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        }),
        ('Related Objects', {
            'fields': ('related_budget_id', 'related_expense_id'),
            'classes': ('collapse',)
        }),
        ('Actions', {
            'fields': ('action_url', 'action_data'),
            'classes': ('collapse',)
        }),
    )
