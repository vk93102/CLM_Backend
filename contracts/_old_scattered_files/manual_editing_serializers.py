"""
Manual Contract Editing - Serializers
"""
from rest_framework import serializers
from .manual_editing_models import (
    ContractEditingSession,
    ContractEditingStep,
    ContractEditingTemplate,
    ContractPreview,
    ContractEdits,
    ContractFieldValidationRule
)


class ContractEditingTemplateSerializer(serializers.ModelSerializer):
    """
    Serialize contract editing template with all form and clause configurations
    """
    class Meta:
        model = ContractEditingTemplate
        fields = [
            'id', 'base_template_id', 'name', 'description', 'category',
            'contract_type', 'form_fields', 'default_values', 'mandatory_clauses',
            'optional_clauses', 'clause_order', 'constraint_templates',
            'contract_content_template', 'styling_config', 'preview_sample',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContractFieldValidationRuleSerializer(serializers.ModelSerializer):
    """
    Serialize field validation rules
    """
    class Meta:
        model = ContractFieldValidationRule
        fields = ['id', 'template', 'field_name', 'rule_type', 'rule_value', 'error_message']
        read_only_fields = ['id']


class ContractEditsSerializer(serializers.ModelSerializer):
    """
    Serialize contract edits
    """
    class Meta:
        model = ContractEdits
        fields = ['id', 'session', 'edit_type', 'field_name', 'old_value', 
                  'new_value', 'edit_reason', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ContractEditingStepSerializer(serializers.ModelSerializer):
    """
    Serialize editing steps
    """
    class Meta:
        model = ContractEditingStep
        fields = ['id', 'session', 'step_type', 'step_data', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ContractPreviewSerializer(serializers.ModelSerializer):
    """
    Serialize contract preview
    """
    class Meta:
        model = ContractPreview
        fields = ['id', 'session', 'preview_html', 'preview_text', 
                  'generated_at', 'form_data_snapshot', 'clauses_snapshot',
                  'constraints_snapshot']
        read_only_fields = ['id', 'generated_at']


class ContractEditingSessionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed session serializer with steps and edits
    """
    steps = ContractEditingStepSerializer(many=True, read_only=True)
    edits = ContractEditsSerializer(many=True, read_only=True)
    preview = ContractPreviewSerializer(read_only=True)
    
    class Meta:
        model = ContractEditingSession
        fields = ['id', 'tenant_id', 'user_id', 'template_id', 'status',
                  'form_data', 'selected_clause_ids', 'custom_clauses',
                  'constraints_config', 'created_at', 'updated_at',
                  'last_saved_at', 'steps', 'edits', 'preview']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_saved_at']


class ContractEditingSessionSerializer(serializers.ModelSerializer):
    """
    Basic session serializer
    """
    class Meta:
        model = ContractEditingSession
        fields = ['id', 'tenant_id', 'user_id', 'template_id', 'status',
                  'form_data', 'selected_clause_ids', 'custom_clauses',
                  'constraints_config', 'created_at', 'updated_at', 'last_saved_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_saved_at']


class FormFieldSubmissionSerializer(serializers.Serializer):
    """
    Validate form field submission
    """
    field_name = serializers.CharField(max_length=255)
    field_value = serializers.JSONField()
    
    def validate(self, data):
        # Additional validation logic can be added here
        return data


class ClauseSelectionSerializer(serializers.Serializer):
    """
    Validate clause selection
    """
    clause_ids = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )
    custom_clause_content = serializers.JSONField(required=False, allow_null=True)
    
    def validate_clause_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one clause must be selected")
        return value


class ConstraintDefinitionSerializer(serializers.Serializer):
    """
    Validate constraint/version definitions
    """
    constraint_name = serializers.CharField(max_length=255)
    constraint_value = serializers.JSONField()
    applies_to_clauses = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class ContractPreviewRequestSerializer(serializers.Serializer):
    """
    Request parameters for generating contract preview
    """
    form_data = serializers.JSONField()
    selected_clause_ids = serializers.ListField(
        child=serializers.CharField()
    )
    custom_clauses = serializers.JSONField(required=False)
    constraints_config = serializers.JSONField(required=False)


class ContractEditAfterPreviewSerializer(serializers.Serializer):
    """
    Validate edits made after preview
    """
    edit_type = serializers.ChoiceField(
        choices=['form_field', 'clause_added', 'clause_removed', 
                 'clause_content_edited', 'constraint_added', 'constraint_modified']
    )
    field_name = serializers.CharField(max_length=255, required=False)
    old_value = serializers.JSONField(required=False, allow_null=True)
    new_value = serializers.JSONField(required=False, allow_null=True)
    edit_reason = serializers.CharField(required=False, max_length=500)


class FinalizedContractSerializer(serializers.Serializer):
    """
    Finalize contract after editing
    """
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, max_length=1000)
    contract_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )
    effective_date = serializers.DateField(required=False)
    expiration_date = serializers.DateField(required=False)
    additional_metadata = serializers.JSONField(required=False)
