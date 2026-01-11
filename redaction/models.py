from django.db import models
import uuid

class RedactionJobModel(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    document_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    patterns = models.JSONField(default=list)
    redacted_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'redaction_jobs'
        app_label = 'redaction'
