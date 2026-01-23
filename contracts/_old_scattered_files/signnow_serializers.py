"""
Serializers for SignNow E-Signature models
"""

from rest_framework import serializers
from .models import ESignatureContract, Signer, SigningAuditLog


class SignerSerializer(serializers.ModelSerializer):
    """Serializer for Signer model"""
    
    class Meta:
        model = Signer
        fields = [
            'id',
            'email',
            'name',
            'signing_order',
            'status',
            'has_signed',
            'signed_at',
            'invited_at',
            'signing_url',
            'signing_url_expires_at',
            'declined_reason',
        ]
        read_only_fields = ['id', 'invited_at', 'signed_at']


class SigningAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for SigningAuditLog model"""
    
    signer_email = serializers.CharField(source='signer.email', read_only=True)
    
    class Meta:
        model = SigningAuditLog
        fields = [
            'id',
            'event',
            'message',
            'signer_email',
            'old_status',
            'new_status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ESignatureContractSerializer(serializers.ModelSerializer):
    """Serializer for ESignatureContract model"""
    
    signers = SignerSerializer(many=True, read_only=True)
    audit_logs = SigningAuditLogSerializer(many=True, read_only=True)
    contract_title = serializers.CharField(source='contract.title', read_only=True)
    
    class Meta:
        model = ESignatureContract
        fields = [
            'id',
            'contract_title',
            'signnow_document_id',
            'status',
            'signing_order',
            'sent_at',
            'completed_at',
            'expires_at',
            'signers',
            'audit_logs',
            'last_status_check_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'signnow_document_id',
            'sent_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
