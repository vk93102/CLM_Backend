from rest_framework import serializers
from .models import Workflow, WorkflowInstance

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowInstance
        fields = '__all__'
