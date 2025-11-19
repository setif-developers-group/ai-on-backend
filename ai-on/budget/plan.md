<PROTOCOL:PLAN>
1.  **Update `budget/models.py`**:
    *   Define `Budget` model with fields:
        *   `user`: ForeignKey to `auth.User` (on_delete=CASCADE).
        *   `title`: CharField (max_length=255).
        *   `budget`: DecimalField (max_digits=10, decimal_places=2).
        *   `spent`: DecimalField (max_digits=10, decimal_places=2, default=0).
        *   `description`: TextField (Markdown content).
        *   `created_at`, `updated_at`: DateTimeFields (auto_now_add/auto_now) for good practice.

2.  **Create `budget/serializers.py`**:
    *   `BudgetSerializer`: Include all fields (`id`, `user`, `title`, `budget`, `spent`, `description`, `created_at`, `updated_at`).
    *   `BudgetListSerializer`: Inherit from `BudgetSerializer` or `ModelSerializer`, exclude `description`.

3.  **Update `budget/views.py`**:
    *   Implement `BudgetViewSet` inheriting from `ModelViewSet`.
    *   Set `permission_classes` to `[IsAuthenticated]`.
    *   Override `get_queryset` to return `Budget.objects.filter(user=self.request.user)`.
    *   Override `get_serializer_class` to use `BudgetListSerializer` for `list` action and `BudgetSerializer` for others.
    *   Add `generate` action (`@action(detail=False, methods=['post'])`) as a placeholder for the AI generation logic.

4.  **Update `budget/urls.py`**:
    *   Define `DefaultRouter`.
    *   Register `BudgetViewSet` with basename `budget`.
    *   Include router URLs.

5.  **Run Migrations**:
    *   `python manage.py makemigrations`
    *   `python manage.py migrate`
</PROTOCOL:PLAN>
