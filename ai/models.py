from django.db import models
import uuid

class AIInferenceModel(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    model_name = models.CharField(max_length=255)
    input_data = models.JSONField(default=dict)
    output = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_inferences'
        app_label = 'ai'


class DraftGenerationTask(models.Model):
    """Track async draft generation tasks"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    user_id = models.UUIDField(db_index=True)
    
    # Task configuration
    task_id = models.CharField(max_length=255, unique=True, db_index=True)  # Celery task ID
    contract_type = models.CharField(max_length=100)
    template_id = models.UUIDField(null=True, blank=True)
    
    # Input parameters
    input_params = models.JSONField(default=dict)
    
    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    generated_text = models.TextField(blank=True)
    citations = models.JSONField(default=list)  # List of source clause IDs
    error_message = models.TextField(blank=True)
    
    # Metadata
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_draft_generation_tasks'
        app_label = 'ai'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['task_id']),
        ]
    
    def __str__(self):
        return f"DraftTask {self.task_id} - {self.status}"


class ClauseAnchor(models.Model):
    """Pre-defined anchor clauses for classification"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Classification info
    label = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=50)  # e.g., "Legal", "Financial", "Operational"
    
    # Example text for this clause type
    example_text = models.TextField()
    
    # Pre-computed embedding (1024-dim for voyage-law-2)
    embedding = models.JSONField(default=list)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_clause_anchors'
        app_label = 'ai'
        ordering = ['category', 'label']
        indexes = [
            models.Index(fields=['label', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.label} ({self.category})"
