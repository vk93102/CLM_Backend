from django.db import models
import uuid

class AuditLogModel(models.Model):
    ACTION_TYPES = [('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('view', 'View')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    user_id = models.UUIDField()
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        app_label = 'audit_logs'
