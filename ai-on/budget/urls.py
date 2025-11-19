from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetGenerateView, BudgetViewSet

router = DefaultRouter()
router.register(r'', BudgetViewSet, basename='budget')

urlpatterns = [
    path('generate/', BudgetGenerateView.as_view(), name='budget-generate'),
    path('', include(router.urls)),
]