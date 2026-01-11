from django.db import models
import uuid

class MetadataFieldModel(models.Model):
    FIELD_TYPES = [('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('select', 'Select'), ('multi_select', 'Multi Select')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'metadata_fields'
        app_label = 'metadata'
