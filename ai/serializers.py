from rest_framework import serializers
from .models import AIInferenceModel, DraftGenerationTask, ClauseAnchor


class AIInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInferenceModel
        fields = '__all__'


class DraftGenerationTaskSerializer(serializers.ModelSerializer):
    """Serializer for async draft generation tasks"""
    
    class Meta:
        model = DraftGenerationTask
        fields = [
            'id',
            'task_id',
            'tenant_id',
            'user_id',
            'contract_type',
            'template_id',
            'input_params',
            'status',
            'generated_text',
            'citations',
            'error_message',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'tenant_id',
            'user_id',
            'task_id',
            'status',
            'generated_text',
            'citations',
            'error_message',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]


class MetadataExtractionSerializer(serializers.Serializer):
    """Serializer for metadata extraction request/response"""
    
    # Request
    document_id = serializers.UUIDField(required=True, write_only=True)
    
    # Response
    parties = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    effective_date = serializers.DateField(read_only=True, allow_null=True)
    termination_date = serializers.DateField(read_only=True, allow_null=True)
    contract_value = serializers.DictField(read_only=True)


class ClauseAnchorSerializer(serializers.ModelSerializer):
    """Serializer for clause anchor definitions"""
    
    class Meta:
        model = ClauseAnchor
        fields = [
            'id',
            'label',
            'description',
            'category',
            'example_text',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClauseClassificationSerializer(serializers.Serializer):
    """Serializer for clause classification request/response"""
    
    # Request
    text = serializers.CharField(required=True, write_only=True)
    
    # Response
    label = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    confidence = serializers.FloatField(read_only=True)
