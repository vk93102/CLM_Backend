"""
SignNow E-Signature API Endpoints

Implements 5 core endpoints:
1. POST /contracts/upload - Upload contract to SignNow
2. POST /esign/send - Send for signature  
3. GET /esign/signing-url/{contract_id} - Get signing URL
4. GET /esign/status/{contract_id} - Poll status
5. GET /esign/executed/{contract_id} - Download executed document
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.utils import timezone
import logging

from contracts.models import Contract, ESignatureContract, Signer, SigningAuditLog
from contracts.signnow_service import SignNowAPIService, SignNowAuthService

logger = logging.getLogger(__name__)
api_service = SignNowAPIService()


# ═══════════════════════════════════════════════════════════════════════════
# 1. UPLOAD CONTRACT TO SIGNNOW
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_contract(request):
    """
    Upload contract PDF to SignNow
    
    Request:
    {
        "contract_id": "uuid",
        "document_name": "Optional name (defaults to contract title)"
    }
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",
        "signnow_document_id": "doc_id",
        "status": "draft",
        "message": "Contract uploaded successfully"
    }
    """
    try:
        contract_id = request.data.get("contract_id")
        if not contract_id:
            return Response(
                {"error": "contract_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get contract
        contract = get_object_or_404(Contract, id=contract_id)
        
        # Check if already has e-signature record
        if hasattr(contract, 'esignature'):
            return Response(
                {
                    "error": "Contract already uploaded for signing",
                    "signnow_document_id": contract.esignature.signnow_document_id,
                    "status": contract.esignature.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get contract PDF from storage
        if not contract.document_r2_key:
            return Response(
                {"error": "No document file found for contract"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pdf_content = default_storage.open(contract.document_r2_key, 'rb').read()
        except Exception as e:
            logger.error(f"Failed to read contract file: {str(e)}")
            return Response(
                {"error": "Failed to read contract file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Upload to SignNow
        document_name = request.data.get("document_name", contract.title)
        signnow_response = api_service.upload_document(pdf_content, document_name)
        
        signnow_document_id = signnow_response.get("id")
        if not signnow_document_id:
            return Response(
                {"error": "Failed to get document ID from SignNow"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create e-signature contract record
        esig = ESignatureContract.objects.create(
            contract=contract,
            signnow_document_id=signnow_document_id,
            status='draft',
            original_r2_key=contract.document_r2_key,
            signing_request_data={"document_name": document_name}
        )
        
        # Log event
        SigningAuditLog.objects.create(
            esignature_contract=esig,
            event='invite_sent',
            message=f'Document uploaded to SignNow: {signnow_document_id}',
            signnow_response=signnow_response,
            new_status='draft'
        )
        
        logger.info(f"Contract {contract_id} uploaded to SignNow: {signnow_document_id}")
        
        return Response(
            {
                "success": True,
                "contract_id": str(contract_id),
                "signnow_document_id": signnow_document_id,
                "status": "draft",
                "message": "Contract uploaded successfully"
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ═══════════════════════════════════════════════════════════════════════════
# 2. SEND FOR SIGNATURE
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_for_signature(request):
    """
    Send document for signatures
    
    Request:
    {
        "contract_id": "uuid",
        "signers": [
            {"email": "signer1@example.com", "name": "Signer 1"},
            {"email": "signer2@example.com", "name": "Signer 2"}
        ],
        "signing_order": "sequential" | "parallel",
        "expires_in_days": 30
    }
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",
        "status": "sent",
        "signers_invited": 2,
        "message": "Invitations sent successfully"
    }
    """
    try:
        contract_id = request.data.get("contract_id")
        signers_data = request.data.get("signers", [])
        signing_order = request.data.get("signing_order", "sequential")
        expires_in_days = request.data.get("expires_in_days", 30)
        
        if not contract_id or not signers_data:
            return Response(
                {"error": "contract_id and signers are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get e-signature contract
        esig = get_object_or_404(ESignatureContract, contract_id=contract_id)
        
        if esig.status != 'draft':
            return Response(
                {"error": f"Contract already sent (status: {esig.status})"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create SignNow invitations
        signnow_invites = api_service.create_invite(
            esig.signnow_document_id,
            signers_data,
            signing_order=signing_order
        )
        
        # Store signer information
        for idx, signer_info in enumerate(signers_data):
            Signer.objects.create(
                esignature_contract=esig,
                email=signer_info["email"],
                name=signer_info.get("name", ""),
                signing_order=idx + 1 if signing_order == "sequential" else 0,
                status='invited'
            )
        
        # Update e-signature contract
        esig.status = 'sent'
        esig.signing_order = signing_order
        esig.sent_at = timezone.now()
        esig.expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        esig.signing_request_data = {
            "signers": signers_data,
            "signing_order": signing_order,
            "expires_in_days": expires_in_days
        }
        esig.save()
        
        # Log event
        SigningAuditLog.objects.create(
            esignature_contract=esig,
            event='invite_sent',
            message=f'Invitations sent to {len(signers_data)} signer(s)',
            signnow_response=signnow_invites,
            old_status='draft',
            new_status='sent'
        )
        
        logger.info(
            f"Sent contract {contract_id} for signature to {len(signers_data)} signers"
        )
        
        return Response(
            {
                "success": True,
                "contract_id": str(contract_id),
                "status": "sent",
                "signers_invited": len(signers_data),
                "expires_at": esig.expires_at.isoformat(),
                "message": "Invitations sent successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Send for signature failed: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. GENERATE SIGNING URL
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_signing_url(request, contract_id):
    """
    Generate embedded signing URL for a specific signer
    
    Query Parameters:
    - signer_email: Email of signer (required)
    
    Response:
    {
        "success": true,
        "signing_url": "https://app.signnow.com/embedded-signing/...",
        "signer_email": "signer@example.com",
        "expires_at": "2026-02-18T..."
    }
    """
    try:
        signer_email = request.query_params.get("signer_email")
        if not signer_email:
            return Response(
                {"error": "signer_email query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get e-signature contract
        esig = get_object_or_404(ESignatureContract, contract_id=contract_id)
        
        # Get signer
        signer = get_object_or_404(Signer, esignature_contract=esig, email=signer_email)
        
        # Generate signing link if not already cached
        if not signer.signing_url or (
            signer.signing_url_expires_at and 
            signer.signing_url_expires_at <= timezone.now()
        ):
            link_response = api_service.get_signing_link(
                esig.signnow_document_id,
                signer_email
            )
            
            signer.signing_url = link_response.get("signing_link")
            signer.signing_url_expires_at = timezone.now() + timezone.timedelta(hours=24)
            signer.save()
        
        return Response(
            {
                "success": True,
                "signing_url": signer.signing_url,
                "signer_email": signer_email,
                "expires_at": signer.signing_url_expires_at.isoformat() if signer.signing_url_expires_at else None,
                "message": "Signing URL generated successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Failed to generate signing URL: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ═══════════════════════════════════════════════════════════════════════════
# 4. CHECK STATUS (POLLING)
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_status(request, contract_id):
    """
    Get document status from database (and optionally update from SignNow)
    
    Response:
    {
        "success": true,
        "contract_id": "uuid",
        "status": "draft" | "sent" | "in_progress" | "completed" | "declined",
        "signers": [
            {
                "email": "signer1@example.com",
                "name": "John Doe",
                "status": "invited" | "viewed" | "in_progress" | "signed" | "declined",
                "signed_at": "2026-02-18T..." or null
            }
        ],
        "all_signed": false,
        "last_checked": "2026-02-18T..."
    }
    """
    try:
        # Get e-signature contract
        esig = get_object_or_404(ESignatureContract, contract_id=contract_id)
        
        # Try to poll SignNow (optional - if fails, just return DB data)
        try:
            status_info = api_service.get_document_status(esig.signnow_document_id)
            
            # Update signer statuses from SignNow
            for signer_status in status_info["signers"]:
                try:
                    signer = Signer.objects.get(
                        esignature_contract=esig,
                        email=signer_status["email"]
                    )
                    
                    old_status = signer.status
                    new_status = signer_status["status"]
                    
                    signer.status = new_status
                    if new_status == "signed":
                        signer.has_signed = True
                        if not signer.signed_at:
                            signer.signed_at = timezone.now()
                    signer.save()
                    
                    # Log status change
                    if old_status != new_status:
                        SigningAuditLog.objects.create(
                            esignature_contract=esig,
                            signer=signer,
                            event='status_checked',
                            message=f'Status changed from {old_status} to {new_status}',
                            old_status=old_status,
                            new_status=new_status
                        )
                        
                except Signer.DoesNotExist:
                    pass
            
            # Update contract status if all signed
            old_contract_status = esig.status
            if status_info["is_completed"]:
                esig.status = "completed"
                if not esig.completed_at:
                    esig.completed_at = timezone.now()
            else:
                esig.status = status_info["status"]
            
            esig.last_status_check_at = timezone.now()
            esig.save()
            
            logger.info(f"Updated status from SignNow for contract {contract_id}: {esig.status}")
            
        except Exception as e:
            # SignNow API failed - just use database data
            logger.warning(f"Could not poll SignNow, using cached data: {str(e)}")
        
        # Build response from database
        signers_response = []
        for signer in esig.signers.all():
            signers_response.append({
                "email": signer.email,
                "name": signer.name,
                "status": signer.status,
                "signed_at": signer.signed_at.isoformat() if signer.signed_at else None,
                "has_signed": signer.has_signed
            })
        
        all_signed = all(s["has_signed"] for s in signers_response)
        
        logger.info(f"Returning status for contract {contract_id}: {esig.status}")
        
        return Response(
            {
                "success": True,
                "contract_id": str(contract_id),
                "status": esig.status,
                "signers": signers_response,
                "all_signed": all_signed,
                "last_checked": esig.last_status_check_at.isoformat() if esig.last_status_check_at else None
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. DOWNLOAD EXECUTED DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_executed_document(request, contract_id):
    """
    Download signed PDF from SignNow and store immutable copy
    
    Response: PDF file download or JSON error
    {
        "error": "Contract not yet completed"
    }
    """
    try:
        # Get e-signature contract
        esig = get_object_or_404(ESignatureContract, id=contract_id)
        
        # If status is not completed, re-poll first
        if esig.status != "completed":
            # Re-check status
            status_info = api_service.get_document_status(esig.signnow_document_id)
            if not status_info["is_completed"]:
                return Response(
                    {
                        "error": "Contract not yet completed by all signers",
                        "current_status": esig.status,
                        "message": "Please try again after all signers have completed"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status
            esig.status = "completed"
            esig.completed_at = timezone.now()
            esig.save()
        
        # Download PDF from SignNow
        pdf_content = api_service.download_document(esig.signnow_document_id)
        
        if not pdf_content:
            return Response(
                {"error": "Failed to download signed document"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Store immutable copy if not already stored
        if not esig.executed_r2_key:
            r2_key = f"signed-contracts/{contract_id}_executed.pdf"
            default_storage.save(r2_key, pdf_content)
            esig.executed_r2_key = r2_key
            esig.save()
        
        # Log download
        SigningAuditLog.objects.create(
            esignature_contract=esig,
            event='document_downloaded',
            message='Executed document downloaded',
            new_status='completed'
        )
        
        logger.info(f"Downloaded executed document for contract {contract_id}")
        
        # Return PDF file
        from django.http import FileResponse
        filename = f"signed_contract_{contract_id}.pdf"
        return FileResponse(
            pdf_content,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
