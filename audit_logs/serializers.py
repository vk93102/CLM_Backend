from rest_framework import serializers
from .models import AuditLogModel

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLogModel
        fields = '__all__'
