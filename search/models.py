from django.db import models
import uuid

class SearchIndexModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_indices'
        app_label = 'search'
