from django.db import models
import uuid

class RuleModel(models.Model):
    RULE_TYPES = [('workflow', 'Workflow'), ('validation', 'Validation'), ('automation', 'Automation')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rules'
        app_label = 'rules'
