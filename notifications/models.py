from django.db import models
import uuid

class NotificationModel(models.Model):
    TYPES = [('email', 'Email'), ('sms', 'SMS'), ('in_app', 'In App')]
    STATUS = [('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    recipient_id = models.UUIDField()
    notification_type = models.CharField(max_length=20, choices=TYPES)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'notifications'
        app_label = 'notifications'
