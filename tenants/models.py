from django.db import models
from django.utils import timezone
import uuid

class TenantModel(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    subscription_plan = models.CharField(max_length=50, default='free')
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        app_label = 'tenants'
