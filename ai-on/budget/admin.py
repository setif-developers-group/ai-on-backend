from django.contrib import admin
from .models import Budget

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'budget', 'spent', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'description')
