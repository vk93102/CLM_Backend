from django.db import models
import uuid

class ApprovalModel(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    requester_id = models.UUIDField()
    approver_id = models.UUIDField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'approvals'
        app_label = 'approvals'
