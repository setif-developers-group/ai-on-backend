from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'title', 'budget', 'spent', 'description', 'created_at', 'updated_at']
        read_only_fields = ['user', 'title', 'description', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Ensure the user is set from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BudgetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'title', 'budget', 'spent', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
