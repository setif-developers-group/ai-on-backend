# Notify Module

The **Notify** module is a centralized notification system for the AION application. All agents can use this service to create and manage user notifications.

## Overview

The Notify module provides a unified way to:
- Create notifications from any agent or service
- Filter notifications by read/unread status
- Mark notifications as read (individually or in bulk)
- Track notification history
- Manage notification priorities and types

## Architecture

### Components

- **`models.py`**: Defines the `Notification` model
- **`serializers.py`**: Handles request/response serialization
- **`services.py`**: Core business logic for notification management
- **`views.py`**: API endpoints for notification CRUD operations
- **`urls.py`**: URL routing
- **`admin.py`**: Django admin interface

### Design Pattern

This is a **service-only module** (no AI agent). Other agents call `create_notification()` to add notifications to the database.

## Notification Model

### Fields

- `user` - The user who receives the notification
- `notification_type` - Type of notification (budget_alert, expense_alert, advisor_tip, goal_milestone, system)
- `priority` - Priority level (low, medium, high, urgent)
- `title` - Notification title
- `message` - Notification message
- `is_read` - Read status (boolean)
- `created_at` - Creation timestamp
- `read_at` - When the notification was read
- `related_budget_id` - Optional link to budget
- `related_expense_id` - Optional link to expense
- `action_url` - Optional URL for frontend navigation
- `action_data` - Optional JSON data for frontend actions

### Notification Types

- **budget_alert**: Budget-related alerts (overspending, etc.)
- **expense_alert**: Expense-related warnings (approaching limit, etc.)
- **advisor_tip**: Tips and recommendations from the advisor
- **goal_milestone**: Goal achievement notifications
- **system**: System-level notifications

### Priority Levels

- **low**: Informational notifications
- **medium**: Standard notifications (default)
- **high**: Important notifications requiring attention
- **urgent**: Critical notifications requiring immediate action

## API Endpoints

### 1. List Notifications

**Endpoint**: `GET /api/notify/`

Get all notifications with optional filtering.

**Query Parameters**:
- `read=true` - Show only read notifications
- `read=false` - Show only unread notifications
- No parameter - Show all notifications

**Request**:
```bash
# Get all notifications
curl -X GET http://localhost:8000/api/notify/ \
  -H "Authorization: Bearer <token>"

# Get only unread notifications
curl -X GET "http://localhost:8000/api/notify/?read=false" \
  -H "Authorization: Bearer <token>"

# Get only read notifications
curl -X GET "http://localhost:8000/api/notify/?read=true" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
[
  {
    "id": 1,
    "notification_type": "budget_alert",
    "priority": "high",
    "title": "⚠️ Overspending in Groceries",
    "message": "You have exceeded your budget for Groceries. Budget: 20000 DZD, Spent: 20500 DZD",
    "is_read": false,
    "created_at": "2025-11-22T03:00:00Z",
    "read_at": null,
    "related_budget_id": 5,
    "related_expense_id": null,
    "action_url": "/budget/5",
    "action_data": null
  }
]
```

---

### 2. Get Notification Details

**Endpoint**: `GET /api/notify/{id}/`

Get a specific notification. **Automatically marks it as read**.

**Request**:
```bash
curl -X GET http://localhost:8000/api/notify/1/ \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "id": 1,
  "notification_type": "budget_alert",
  "priority": "high",
  "title": "⚠️ Overspending in Groceries",
  "message": "You have exceeded your budget...",
  "is_read": true,
  "created_at": "2025-11-22T03:00:00Z",
  "read_at": "2025-11-22T03:05:00Z",
  "related_budget_id": 5,
  "related_expense_id": null,
  "action_url": "/budget/5",
  "action_data": null
}
```

---

### 3. Mark Notification as Read

**Endpoint**: `PATCH /api/notify/{id}/read/`

Manually mark a specific notification as read.

**Request**:
```bash
curl -X PATCH http://localhost:8000/api/notify/1/read/ \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "id": 1,
  "is_read": true,
  "read_at": "2025-11-22T03:05:00Z",
  ...
}
```

---

### 4. Mark All as Read

**Endpoint**: `POST /api/notify/mark-all-read/`

Mark all unread notifications as read.

**Request**:
```bash
curl -X POST http://localhost:8000/api/notify/mark-all-read/ \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "marked_count": 5
}
```

---

### 5. Get Unread Count

**Endpoint**: `GET /api/notify/unread-count/`

Get the count of unread notifications (useful for badge display).

**Request**:
```bash
curl -X GET http://localhost:8000/api/notify/unread-count/ \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "unread_count": 3
}
```

---

### 6. Delete Notification

**Endpoint**: `DELETE /api/notify/{id}/delete/`

Delete a specific notification.

**Request**:
```bash
curl -X DELETE http://localhost:8000/api/notify/1/delete/ \
  -H "Authorization: Bearer <token>"
```

**Response**: `204 No Content`

---

## Integration Guide

### For Agent Developers

To create notifications from your agent, import and use the `create_notification` function:

```python
from notify.services import create_notification

# Example: Budget overspending alert
create_notification(
    user=user,
    notification_type='budget_alert',
    priority='high',
    title='⚠️ Overspending in Groceries',
    message='You have exceeded your budget for Groceries. Budget: 20000 DZD, Spent: 20500 DZD',
    related_budget_id=budget.id,
    action_url=f'/budget/{budget.id}'
)

# Example: Expense warning (80% threshold)
create_notification(
    user=user,
    notification_type='expense_alert',
    priority='medium',
    title='📊 Approaching budget limit: Entertainment',
    message='You have used 85% of your Entertainment budget. Remaining: 3000 DZD',
    related_budget_id=budget.id
)

# Example: Advisor tip
create_notification(
    user=user,
    notification_type='advisor_tip',
    priority='low',
    title='💡 Smart Purchase Tip',
    message='Consider saving for 2 more months to afford this purchase without impacting your emergency fund.'
)
```

### Service Functions

Available functions in `notify.services`:

- `create_notification(user, notification_type, title, message, priority='medium', **kwargs)` - Create a notification
- `mark_as_read(notification_id, user)` - Mark as read
- `mark_all_as_read(user)` - Mark all as read
- `get_unread_count(user)` - Get unread count
- `get_notifications(user, is_read=None, limit=None)` - Get notifications with filtering
- `delete_old_notifications(days=30)` - Cleanup old notifications

---

## Current Integrations

### Expense Manager

The expense manager creates notifications for:
- **Overspending** (high priority): When budget is exceeded
- **Budget warnings** (medium priority): When 80% of budget is used

### Budget Agent

(To be integrated) Will create notifications for:
- Budget rebalancing
- Budget deletions
- Budget updates

### Advisor Agent

(To be integrated) Can create notifications for:
- Purchase recommendations
- Smart tips
- Savings suggestions

---

## Best Practices

### For Backend Developers

1. **Choose appropriate priority**:
   - `urgent`: Critical issues requiring immediate action
   - `high`: Important alerts (overspending, etc.)
   - `medium`: Standard notifications (warnings, tips)
   - `low`: Informational messages

2. **Use emojis in titles** for visual appeal:
   - ⚠️ for alerts
   - 📊 for analytics/stats
   - 💡 for tips
   - 🎉 for achievements
   - ℹ️ for information

3. **Include action URLs** when relevant for deep linking

4. **Link related objects** using `related_budget_id` or `related_expense_id`

### For Frontend Developers

1. **Display unread count** using `/api/notify/unread-count/`
2. **Filter by read status** using query parameters
3. **Auto-refresh** notification list periodically
4. **Handle action URLs** for navigation on click
5. **Show priority visually** with colors/icons
6. **Group by type** for better organization

---

## Cleanup

Old notifications can be cleaned up using:

```python
from notify.services import delete_old_notifications

# Delete notifications older than 30 days
deleted_count = delete_old_notifications(days=30)
```

This can be run as a periodic task (e.g., daily cron job).

---

## Future Enhancements

Potential improvements:
- Push notifications (web push, mobile)
- Email notifications
- Notification preferences (per type/priority)
- Notification grouping
- Rich media support (images, links)
- Scheduled notifications
- Notification templates
