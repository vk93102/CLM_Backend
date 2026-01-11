from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid

class Workflow(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(max_length=100, default='approval')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    steps = models.JSONField(default=list)
    config = models.JSONField(default=dict)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflows'

class WorkflowInstance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    entity_id = models.UUIDField()
    entity_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflow_instances'
