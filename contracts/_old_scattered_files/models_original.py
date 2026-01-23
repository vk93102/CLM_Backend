"""
Contract and Workflow models with tenant isolation
"""
from django.db import models
import uuid


class ContractTemplate(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    r2_key = models.CharField(max_length=500)
    merge_fields = models.JSONField(default=list)
    mandatory_clauses = models.JSONField(default=list)
    business_rules = models.JSONField(default=dict)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contract_templates'
        ordering = ['-created_at']
        unique_together = [('tenant_id', 'name', 'version')]
        indexes = [
            models.Index(fields=['tenant_id', 'contract_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class Clause(models.Model):
    """Reusable contract clause with versioning"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    clause_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    contract_type = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_mandatory = models.BooleanField(default=False)
    alternatives = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    source_template = models.CharField(max_length=255, blank=True, null=True)
    source_template_version = models.IntegerField(null=True, blank=True)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clauses'
        ordering = ['-created_at']
        unique_together = [('tenant_id', 'clause_id', 'version')]
        indexes = [
            models.Index(fields=['tenant_id', 'contract_type']),
            models.Index(fields=['clause_id']),
        ]
    
    def __str__(self):
        return f"{self.clause_id} v{self.version}"
    
    def __str__(self):
        return f"{self.clause_id} v{self.version}: {self.name}"


class Contract(models.Model):
    """
    Contract model with tenant isolation for RLS
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True, help_text='Tenant ID for RLS')
    template = models.ForeignKey(
        ContractTemplate,
        on_delete=models.PROTECT,
        related_name='contracts',
        null=True,
        blank=True,
        help_text='Source template used to generate this contract'
    )
    title = models.CharField(max_length=255, help_text='Contract title')
    current_version = models.IntegerField(default=1, help_text='Current version number')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Contract workflow status'
    )
    is_approved = models.BooleanField(default=False, help_text='Explicit approval flag')
    approved_by = models.UUIDField(null=True, blank=True, help_text='User ID who approved')
    approved_at = models.DateTimeField(null=True, blank=True, help_text='Approval timestamp')
    created_by = models.UUIDField(help_text='User ID who created the contract')
    counterparty = models.CharField(max_length=255, blank=True, null=True, help_text='Counterparty name')
    contract_type = models.CharField(max_length=100, blank=True, null=True, help_text='Type of contract (NDA, MSA, etc.)')
    value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text='Contract value')
    start_date = models.DateField(blank=True, null=True, help_text='Contract start date')
    end_date = models.DateField(blank=True, null=True, help_text='Contract end date')
    form_inputs = models.JSONField(default=dict, help_text='Structured intake form inputs')
    user_instructions = models.TextField(blank=True, null=True, help_text='Optional user instructions')
    approval_chain = models.JSONField(default=dict, help_text='Approval chain configuration')
    approval_required = models.BooleanField(default=False, help_text='Is approval required?')
    current_approvers = models.JSONField(default=list, help_text='Current approvers')
    document_r2_key = models.CharField(max_length=500, blank=True, null=True, help_text='R2 storage key for document')
    last_edited_at = models.DateTimeField(blank=True, null=True, help_text='Last edited timestamp')
    last_edited_by = models.UUIDField(blank=True, null=True, help_text='User ID who last edited')
    description = models.TextField(blank=True, null=True, help_text='Contract description')
    metadata = models.JSONField(default=dict, help_text='Additional metadata')
    clauses = models.JSONField(default=list, help_text='List of contract clauses and constraints')
    signed = models.JSONField(default=dict, help_text='Signature information from SignNow with signer names')
    signed_pdf = models.BinaryField(null=True, blank=True, help_text='Signed PDF from SignNow with user signature')
    signnow_document_id = models.CharField(max_length=255, null=True, blank=True, help_text='SignNow document ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'status']),
            models.Index(fields=['tenant_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.status})"


class ContractVersion(models.Model):
    """
    Immutable contract version with document and provenance tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text='Parent contract'
    )
    version_number = models.IntegerField(help_text='Version number')
    r2_key = models.CharField(max_length=500, help_text='R2 storage key for DOCX')
    template_id = models.UUIDField(help_text='Template ID used')
    template_version = models.IntegerField(help_text='Template version used')
    change_summary = models.TextField(blank=True, null=True, help_text='Summary of changes')
    created_by = models.UUIDField(help_text='User ID who created this version')
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(null=True, blank=True, help_text='File size in bytes')
    file_hash = models.CharField(max_length=64, null=True, blank=True, help_text='SHA-256 hash')
    
    class Meta:
        db_table = 'contract_versions'
        ordering = ['-version_number']
        unique_together = [('contract', 'version_number')]
        indexes = [
            models.Index(fields=['contract', 'version_number']),
        ]
    
    def __str__(self):
        return f"{self.contract.title} v{self.version_number}"


class ContractClause(models.Model):
    """
    Junction table for contract-clause relationship with provenance
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_version = models.ForeignKey(
        ContractVersion,
        on_delete=models.CASCADE,
        related_name='clauses',
        help_text='Contract version this clause belongs to'
    )
    clause_id = models.CharField(max_length=100, help_text='Clause identifier')
    clause_version = models.IntegerField(help_text='Clause version used')
    clause_name = models.CharField(max_length=255, help_text='Clause name (denormalized)')
    clause_content = models.TextField(help_text='Clause content (snapshot)')
    is_mandatory = models.BooleanField(default=False, help_text='Was this clause mandatory?')
    position = models.IntegerField(help_text='Clause position in contract')
    alternatives_suggested = models.JSONField(default=list, help_text='Alternative clauses suggested')
    
    class Meta:
        db_table = 'contract_clauses'
        ordering = ['position']
        indexes = [
            models.Index(fields=['contract_version', 'position']),
            models.Index(fields=['clause_id']),
        ]
    
    def __str__(self):
        return f"{self.clause_id} v{self.clause_version} in {self.contract_version}"


class GenerationJob(models.Model):
    """
    Async contract generation job tracking
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='generation_jobs',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, help_text='Progress percentage (0-100)')
    error_message = models.TextField(null=True, blank=True, help_text='Error details if failed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'generation_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.id}: {self.status}"


class BusinessRule(models.Model):
    """
    Business rules for contract validation and clause suggestions
    """
    RULE_TYPE_CHOICES = [
        ('mandatory_clause', 'Mandatory Clause'),
        ('clause_suggestion', 'Clause Suggestion'),
        ('validation', 'Validation Rule'),
        ('restriction', 'Restriction Rule'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True, help_text='Tenant ID for RLS')
    name = models.CharField(max_length=255, help_text='Rule name')
    description = models.TextField(help_text='Rule description')
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES, help_text='Type of rule')
    contract_types = models.JSONField(default=list, help_text='Applicable contract types (empty = all)')
    conditions = models.JSONField(help_text='Rule conditions in JSON format: {"contract_value__gte": 10000000, "contract_type": "MSA"}')
    action = models.JSONField(help_text='Action to take: {"type": "require_clause", "clause_id": "LIAB-001", "message": "Liability clause required for high-value contracts"}')
    priority = models.IntegerField(default=0, help_text='Rule priority (higher = evaluated first)')
    is_active = models.BooleanField(default=True, help_text='Is this rule active?')
    created_by = models.UUIDField(help_text='User ID who created the rule')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_rules'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['tenant_id', 'rule_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class WorkflowLog(models.Model):
    """
    Audit log for contract workflow actions
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('executed', 'Executed'),
        ('deleted', 'Deleted'),
        ('version_created', 'Version Created'),
        ('clause_added', 'Clause Added'),
        ('clause_removed', 'Clause Removed'),
        ('clause_updated', 'Clause Updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='workflow_logs',
        help_text='Related contract'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Action performed'
    )
    performed_by = models.UUIDField(help_text='User ID who performed the action')
    comment = models.TextField(blank=True, null=True, help_text='Optional comment/reason')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True, help_text='Additional metadata')
    
    class Meta:
        db_table = 'workflow_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['contract', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.contract.title} - {self.action} at {self.timestamp}"

# SignNow E-Signature Models

class SignNowCredential(models.Model):
    """
    OAuth 2.0 credentials for SignNow service account (singleton)
    Stores the service account's OAuth tokens for API authentication
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # OAuth Token Fields
    access_token = models.TextField(help_text='Current OAuth access token')
    refresh_token = models.TextField(help_text='OAuth refresh token for renewing access')
    token_expires_at = models.DateTimeField(help_text='When the access token expires')
    
    # Service Account Identity
    client_id = models.CharField(max_length=500, help_text='SignNow OAuth client ID')
    client_secret = models.CharField(max_length=500, help_text='SignNow OAuth client secret')
    account_name = models.CharField(max_length=255, help_text='Service account display name')
    account_id = models.CharField(max_length=255, help_text='SignNow service account ID')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_refreshed_at = models.DateTimeField(null=True, blank=True, help_text='Last token refresh time')
    
    class Meta:
        db_table = 'signnow_credentials'
        verbose_name_plural = 'SignNow Credentials'
    
    def __str__(self):
        return f"SignNow Service Account: {self.account_name}"


class ESignatureContract(models.Model):
    """
    Maps a CLM Contract to a SignNow document for e-signature workflow
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent for Signature'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]
    
    SIGNING_ORDER_CHOICES = [
        ('sequential', 'Sequential'),
        ('parallel', 'Parallel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='esignature_contract',
        help_text='Associated CLM contract'
    )
    
    # SignNow Document Reference
    signnow_document_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='SignNow document ID'
    )
    
    # Signing Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        help_text='Current signing status'
    )
    signing_order = models.CharField(
        max_length=20,
        choices=SIGNING_ORDER_CHOICES,
        default='parallel',
        help_text='Sequential or parallel signing'
    )
    
    # Timeline
    sent_at = models.DateTimeField(null=True, blank=True, help_text='When sent for signature')
    completed_at = models.DateTimeField(null=True, blank=True, help_text='When all signers completed')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Signing deadline')
    last_status_check_at = models.DateTimeField(null=True, blank=True, help_text='Last status polling time')
    
    # Storage References
    original_r2_key = models.CharField(
        max_length=500,
        help_text='Original contract PDF in R2'
    )
    executed_r2_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text='Signed contract PDF in R2'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'esignature_contracts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['signnow_document_id']),
            models.Index(fields=['status']),
            models.Index(fields=['contract', 'status']),
        ]
    
    def __str__(self):
        return f"ESignature: {self.contract.title} ({self.status})"


class Signer(models.Model):
    """
    Email-based signer for an e-signature contract
    Signers are identified by email, not user accounts
    """
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('viewed', 'Viewed'),
        ('in_progress', 'In Progress'),
        ('signed', 'Signed'),
        ('declined', 'Declined'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    esignature_contract = models.ForeignKey(
        ESignatureContract,
        on_delete=models.CASCADE,
        related_name='signers',
        help_text='Associated e-signature contract'
    )
    
    # Signer Identity (Email-based, no user account)
    email = models.EmailField(help_text='Signer email address')
    name = models.CharField(max_length=255, help_text='Signer full name')
    
    # Signing Order
    signing_order = models.IntegerField(help_text='Order in signing sequence (1-based)')
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited',
        db_index=True,
        help_text='Current signing status'
    )
    has_signed = models.BooleanField(default=False, help_text='Whether signer completed')
    signed_at = models.DateTimeField(null=True, blank=True, help_text='When signer completed')
    
    # Signing URL Management
    signing_url = models.TextField(null=True, blank=True, help_text='Embedded signing URL')
    signing_url_expires_at = models.DateTimeField(null=True, blank=True, help_text='URL expiration (24h)')
    
    # Decline Tracking
    declined_reason = models.TextField(null=True, blank=True, help_text='Reason if declined')
    
    # Metadata
    invited_at = models.DateTimeField(auto_now_add=True, help_text='When invitation sent')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'signers'
        ordering = ['signing_order', 'email']
        unique_together = [('esignature_contract', 'email')]
        indexes = [
            models.Index(fields=['esignature_contract', 'status']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.status}) - {self.esignature_contract.contract.title}"


class SigningAuditLog(models.Model):
    """
    Immutable audit trail of all e-signature events
    """
    EVENT_CHOICES = [
        ('invite_sent', 'Invitation Sent'),
        ('document_viewed', 'Document Viewed'),
        ('signing_started', 'Signing Started'),
        ('signing_completed', 'Signing Completed'),
        ('signing_declined', 'Signing Declined'),
        ('status_checked', 'Status Checked'),
        ('document_downloaded', 'Document Downloaded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    esignature_contract = models.ForeignKey(
        ESignatureContract,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text='Associated e-signature contract'
    )
    signer = models.ForeignKey(
        Signer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='Associated signer (if applicable)'
    )
    
    # Event Details
    event = models.CharField(
        max_length=50,
        choices=EVENT_CHOICES,
        db_index=True,
        help_text='Event type'
    )
    message = models.TextField(help_text='Event description')
    
    # Status Transitions
    old_status = models.CharField(max_length=20, null=True, blank=True, help_text='Previous status')
    new_status = models.CharField(max_length=20, null=True, blank=True, help_text='New status')
    
    # SignNow Response
    signnow_response = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text='Full SignNow API response'
    )
    
    # Timestamp (immutable)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'signing_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['esignature_contract', 'created_at']),
            models.Index(fields=['event', 'created_at']),
        ]
        # Make all fields read-only after creation
        permissions = [
            ('view_signing_audit_log', 'Can view signing audit logs'),
        ]
    
    def __str__(self):
        return f"{self.event} - {self.esignature_contract.contract.title} at {self.created_at}"