from django.db import models
import uuid

class OCRJobModel(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    document_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extracted_text = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'ocr_jobs'
        app_label = 'ocr'
