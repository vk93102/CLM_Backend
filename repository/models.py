from django.db import models
import uuid

class RepositoryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=100)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'repository'
        app_label = 'repository'

class RepositoryFolderModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField()
    name = models.CharField(max_length=255)
    parent_id = models.UUIDField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'repository_folders'
        app_label = 'repository'
