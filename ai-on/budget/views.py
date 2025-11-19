from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Budget
from .serializers import BudgetSerializer, BudgetListSerializer
from .services import process_budget_generation, process_budget_update, process_budget_deletion

class BudgetGenerateView(APIView):
    """
    Endpoint to generate budgets using AI based on user profile and history.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: BudgetSerializer(many=True)},
        description="Generate budgets using AI based on user profile and history."
    )
    def post(self, request):
        result = process_budget_generation(request.user)
        if result['type'] == 'success':
            return Response(result['data'], status=status.HTTP_200_OK)
        else:
            return Response(result['data'], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BudgetListSerializer
        return BudgetSerializer

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Manual creation not allowed. Use generate.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_update(self, serializer):
        # We need to check what changed before saving, or check validated_data
        validated_data = serializer.validated_data
        instance = serializer.instance
        
        # Check if budget or spent is changing
        budget_changing = 'budget' in validated_data and validated_data['budget'] != instance.budget
        spent_changing = 'spent' in validated_data and validated_data['spent'] != instance.spent
        
        # Perform the update
        updated_instance = serializer.save()
        
        # Trigger events
        if budget_changing:
            process_budget_update(self.request.user, updated_instance, change_type='budget_change')
            
        if spent_changing:
            if updated_instance.spent > updated_instance.budget:
                process_budget_update(self.request.user, updated_instance, change_type='overspending')

    def perform_destroy(self, instance):
        user = self.request.user
        instance.delete()
        # Trigger rebalancing after deletion
        process_budget_deletion(user)
