from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class agentModel(models.Model):
    """
    Data model for AI agents. Contains only configuration data.
    Business logic is handled in services.py to avoid circular dependencies.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    system_instruction = models.TextField()
    gemini_model = models.CharField(max_length=100)
    thinking_budget = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
        
    
        

class ConversationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Using consistent snake_case for both key and label for readability
    AGENT_CHOICES = [
        ('onboarding_agent', 'onboarding_agent'),
        ('chatbot_agent', 'chatbot_agent'),
        ('main_ai_coordinator', 'main_ai_coordinator'),
        ('market_watcher', 'market_watcher'),
        ('planner_forecaster', 'planner_forecaster'),
        ('receipt_parser', 'receipt_parser'),
        ('product_advisor', 'product_advisor'),
        ('notification_agent', 'notification_agent'),
        ('expense_manager', 'expense_manager'),
        ('budget_agent', 'budget_agent'),
    ]

    agent = models.ForeignKey(
        agentModel,
        on_delete=models.CASCADE,) 
    
    
    role = models.CharField(max_length=10, choices=[('user', 'user'), ('model', 'model')])
    
    # This JSONField stores the entire Content object (message/function call/function response)
    content_data = models.JSONField() 
    
    # Timestamp to ensure correct ordering when loading
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"ConversationHistory(id={self.id}, user={self.user.username}, agent={self.agent}, role={self.role})"
    