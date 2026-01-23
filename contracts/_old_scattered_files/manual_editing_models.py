"""
Manual Contract Editing System - Models
Allows users to create contracts by selecting templates, filling forms, and customizing clauses
"""
from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class ContractEditingSession(models.Model):
    """
    Track user's contract editing session
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    user_id = models.UUIDField()
    template_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    form_data = models.JSONField(default=dict, help_text='User-filled form data')
    selected_clause_ids = models.JSONField(default=list, help_text='User-selected clause IDs')
    custom_clauses = models.JSONField(default=dict, help_text='Custom clause content by user')
    constraints_config = models.JSONField(default=dict, help_text='Constraint/version definitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_saved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'contract_editing_sessions'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['tenant_id', 'user_id']),
            models.Index(fields=['status', 'updated_at']),
        ]
    
    def __str__(self):
        return f"Session {self.id[:8]} - {self.status}"


class ContractEditingStep(models.Model):
    """
    Track each step of contract editing for audit and recovery
    """
    STEP_TYPES = [
        ('template_selection', 'Template Selected'),
        ('form_fill', 'Form Field Filled'),
        ('clause_selection', 'Clause Selected'),
        ('clause_removal', 'Clause Removed'),
        ('clause_customization', 'Clause Customized'),
        ('constraint_definition', 'Constraint Defined'),
        ('preview_generated', 'Preview Generated'),
        ('field_edited', 'Field Edited After Preview'),
        ('saved', 'Draft Saved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ContractEditingSession,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    step_type = models.CharField(max_length=30, choices=STEP_TYPES)
    step_data = models.JSONField(help_text='Data for this step')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contract_editing_steps'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session.id[:8]} - {self.step_type}"


class ContractEditingTemplate(models.Model):
    """
    Extended template for manual editing with form field definitions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_template_id = models.UUIDField(help_text='ID of base ContractTemplate')
    tenant_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default='general')
    contract_type = models.CharField(max_length=100)
    
    # Form Field Configuration
    form_fields = models.JSONField(
        default=dict,
        help_text="""Form field definitions like:
        {
            "party_a_name": {
                "label": "Your Company Name",
                "type": "text",
                "required": true,
                "placeholder": "Enter your company name",
                "validation": {"min_length": 2, "max_length": 255}
            },
            "party_b_name": {
                "label": "Counterparty Name",
                "type": "text",
                "required": true
            },
            "contract_value": {
                "label": "Contract Value (USD)",
                "type": "number",
                "required": true,
                "min": 0,
                "max": 999999999
            }
        }"""
    )
    
    # Default form values
    default_values = models.JSONField(default=dict, help_text='Default values for form fields')
    
    # Clause configuration
    mandatory_clauses = models.JSONField(default=list, help_text='List of mandatory clause IDs')
    optional_clauses = models.JSONField(default=list, help_text='List of optional clause IDs')
    clause_order = models.JSONField(default=list, help_text='Suggested clause order')
    
    # Constraint templates
    constraint_templates = models.JSONField(
        default=dict,
        help_text="""Predefined constraints users can apply:
        {
            "payment_terms": {
                "label": "Payment Terms",
                "options": ["Net 30", "Net 60", "Net 90", "Immediate"],
                "default": "Net 30"
            },
            "jurisdiction": {
                "label": "Governing Jurisdiction",
                "options": ["California", "New York", "Delaware", "Federal"],
                "default": "California"
            }
        }"""
    )
    
    # Contract content template
    contract_content_template = models.TextField(
        help_text='Base contract template with {{placeholders}} for form fields'
    )
    
    # Professional styling
    styling_config = models.JSONField(
        default=dict,
        help_text='Professional styling for generated contracts'
    )
    
    preview_sample = models.TextField(blank=True, help_text='Sample preview of contract')
    
    is_active = models.BooleanField(default=True)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contract_editing_templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'is_active']),
            models.Index(fields=['contract_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.contract_type})"


class ContractPreview(models.Model):
    """
    Store generated contract previews
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(
        ContractEditingSession,
        on_delete=models.CASCADE,
        related_name='preview'
    )
    preview_html = models.TextField(help_text='HTML preview of contract')
    preview_text = models.TextField(help_text='Plain text version of contract')
    generated_at = models.DateTimeField(auto_now_add=True)
    form_data_snapshot = models.JSONField(help_text='Snapshot of form data used for preview')
    clauses_snapshot = models.JSONField(help_text='Snapshot of selected clauses')
    constraints_snapshot = models.JSONField(help_text='Snapshot of constraints used')
    
    class Meta:
        db_table = 'contract_previews'
        indexes = [
            models.Index(fields=['session']),
        ]
    
    def __str__(self):
        return f"Preview for session {self.session.id[:8]}"


class ContractFieldValidationRule(models.Model):
    """
    Define validation rules for contract fields
    """
    RULE_TYPES = [
        ('regex', 'Regular Expression'),
        ('min_value', 'Minimum Value'),
        ('max_value', 'Maximum Value'),
        ('length', 'String Length'),
        ('custom', 'Custom Validation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ContractEditingTemplate,
        on_delete=models.CASCADE,
        related_name='field_validations'
    )
    field_name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    rule_value = models.JSONField(help_text='Rule configuration')
    error_message = models.CharField(max_length=500)
    
    class Meta:
        db_table = 'contract_field_validation_rules'
        unique_together = [('template', 'field_name', 'rule_type')]
    
    def __str__(self):
        return f"{self.field_name} - {self.rule_type}"


class ContractEdits(models.Model):
    """
    Track edits made after preview
    """
    EDIT_TYPES = [
        ('form_field', 'Form Field Edited'),
        ('clause_added', 'Clause Added'),
        ('clause_removed', 'Clause Removed'),
        ('clause_content_edited', 'Clause Content Edited'),
        ('constraint_added', 'Constraint Added'),
        ('constraint_modified', 'Constraint Modified'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ContractEditingSession,
        on_delete=models.CASCADE,
        related_name='edits'
    )
    edit_type = models.CharField(max_length=30, choices=EDIT_TYPES)
    field_name = models.CharField(max_length=255, blank=True)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    edit_reason = models.TextField(blank=True, help_text='Why the user made this edit')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contract_edits'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session.id[:8]} - {self.edit_type}"
