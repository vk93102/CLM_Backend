from rest_framework import serializers
from .models import ApprovalModel

class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalModel
        fields = '__all__'
