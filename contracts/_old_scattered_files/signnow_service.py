"""
SignNow OAuth and API Service Layer

Handles all interactions with SignNow API:
- OAuth token management and auto-refresh
- Document upload
- Invitation creation
- Status polling
- Document download
- URL generation for embedded signing

All operations use cached OAuth token (backend-only auth).
"""

import requests
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# SignNow API Configuration
SIGNNOW_API_BASE = "https://api.signnow.com"
SIGNNOW_AUTH_URL = "https://app.signnow.com/oauth2/authorize"
SIGNNOW_TOKEN_URL = "https://api.signnow.com/oauth2/token"

# OAuth Scopes
SIGNNOW_SCOPES = [
    "document_read",
    "document_write",
    "document_download",
    "invite_read",
    "invite_write",
    "user_read",
]


class SignNowAuthService:
    """
    Manages SignNow OAuth token lifecycle
    """
    
    CACHE_KEY_TOKEN = "signnow_access_token"
    CACHE_KEY_REFRESH = "signnow_refresh_token"
    
    def __init__(self):
        # Get credentials from database instead of environment variables
        from .models import SignNowCredential
        cred = SignNowCredential.objects.first()
        if cred:
            self.client_id = cred.client_id
            self.client_secret = cred.client_secret
            logger.info(f"Loaded SignNow credentials from database: {cred.client_id[:20]}...")
        else:
            # Fallback to environment variables if no database credential
            self.client_id = os.getenv("SIGNNOW_CLIENT_ID")
            self.client_secret = os.getenv("SIGNNOW_CLIENT_SECRET")
            logger.warning("No SignNow credential in database, using environment variables")
        self.redirect_uri = os.getenv("SIGNNOW_REDIRECT_URI", "http://localhost:11000/api/signnow/callback/")
    
    def get_access_token(self):
        """
        Get cached access token or refresh if expired
        Returns: (token, is_fresh)
        """
        # Try cache first
        token = cache.get(self.CACHE_KEY_TOKEN)
        if token:
            logger.info("Using cached SignNow access token")
            return token, False
        
        # Try to refresh
        refreshed_token = self.refresh_token()
        if refreshed_token:
            logger.info("Refreshed SignNow access token")
            return refreshed_token, True
        
        logger.error("Could not obtain SignNow access token")
        raise Exception("SignNow authentication failed - no valid token")
    
    def refresh_token(self):
        """
        Refresh OAuth token using refresh_token
        Returns: access_token or None
        """
        from .models import SignNowCredential
        
        try:
            cred = SignNowCredential.objects.first()
            if not cred or not cred.refresh_token:
                logger.error("No SignNow credential with refresh token")
                return None
            
            # Call SignNow token endpoint
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": cred.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            response = requests.post(
                SIGNNOW_TOKEN_URL,
                data=payload,  # Use 'data' for form encoding (not json)
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            access_token = data.get("access_token")
            new_refresh_token = data.get("refresh_token", cred.refresh_token)
            expires_in = data.get("expires_in", 3600)
            
            # Update credential
            cred.access_token = access_token
            cred.refresh_token = new_refresh_token
            cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            cred.save()
            
            # Cache token
            cache.set(self.CACHE_KEY_TOKEN, access_token, expires_in - 300)  # 5 min buffer
            
            logger.info("Successfully refreshed SignNow token")
            return access_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None
    
    def set_initial_token(self, access_token, refresh_token=None, expires_in=3600):
        """
        Store initial OAuth token after first authentication
        """
        from .models import SignNowCredential
        
        try:
            cred = SignNowCredential.objects.first()
            if not cred:
                logger.error("No SignNow credential to update")
                return False
            
            cred.access_token = access_token
            if refresh_token:
                cred.refresh_token = refresh_token
            cred.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            cred.save()
            
            # Cache token
            cache.set(self.CACHE_KEY_TOKEN, access_token, expires_in - 300)
            
            logger.info("Stored initial SignNow token")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store initial token: {str(e)}")
            return False


class SignNowAPIService:
    """
    Handles all SignNow API operations
    """
    
    def __init__(self):
        self.auth_service = SignNowAuthService()
        self.base_url = SIGNNOW_API_BASE
    
    def _get_headers(self):
        """Get authorization headers with current access token"""
        token, _ = self.auth_service.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    def _request(self, method, endpoint, **kwargs):
        """
        Make authenticated request to SignNow API
        Handles error responses and logging
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            
            # Log request
            logger.info(f"SignNow API: {method} {endpoint} -> {response.status_code}")
            
            # Check for errors
            if response.status_code >= 400:
                logger.error(
                    f"SignNow API Error: {response.status_code}\n"
                    f"URL: {url}\n"
                    f"Response: {response.text}"
                )
                response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SignNow API request failed: {str(e)}")
            raise
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DOCUMENT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def upload_document(self, pdf_file, document_name):
        """
        Upload PDF document to SignNow
        
        Args:
            pdf_file: Binary PDF content
            document_name: Name for the document in SignNow
        
        Returns:
            {
                'id': 'doc_id',
                'document_id': 'doc_id',
                'owner_id': 'owner_id',
                'pages': [...]
            }
        """
        files = {
            'file': (f"{document_name}.pdf", pdf_file, 'application/pdf')
        }
        
        response = self._request(
            "POST",
            "/v2/documents",
            files=files
        )
        
        data = response.json()
        logger.info(f"Uploaded document to SignNow: {data.get('id')}")
        return data
    
    def get_document_details(self, document_id):
        """
        Get document details from SignNow
        
        Returns:
            {
                'id': 'doc_id',
                'owner_id': 'owner_id',
                'pages': [...],
                'invitations': [...],
                'status': 'completed' | 'pending' | ...
            }
        """
        response = self._request(
            "GET",
            f"/v2/documents/{document_id}"
        )
        
        return response.json()
    
    def download_document(self, document_id):
        """
        Download executed PDF from SignNow
        
        Returns: Binary PDF content
        """
        response = self._request(
            "GET",
            f"/v2/documents/{document_id}/download"
        )
        
        return response.content
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INVITATION OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_invite(self, document_id, signers, signing_order="sequential"):
        """
        Create signature invitation(s) for document
        
        Args:
            document_id: SignNow document ID
            signers: List of signer dicts
                [
                    {"email": "signer@example.com", "name": "Signer Name", "order": 1},
                    ...
                ]
            signing_order: "sequential" or "parallel"
        
        Returns:
            Invitation response with invite IDs
        """
        payload = {
            "to": [
                {
                    "email": signer["email"],
                    "role_id": str(i + 1),  # SignNow role ID
                    "order": signer.get("order", i + 1) if signing_order == "sequential" else 0,
                    "name": signer.get("name", ""),
                }
                for i, signer in enumerate(signers)
            ],
            "from": "service_account@company.com",  # Service account sender
            "subject": "Please sign this document",
            "message": "Please review and sign the attached document.",
        }
        
        response = self._request(
            "POST",
            f"/v2/documents/{document_id}/invites",
            json=payload
        )
        
        data = response.json()
        logger.info(f"Created invitation for document {document_id}")
        return data
    
    def get_invite_status(self, invite_id):
        """
        Get status of a specific invitation
        
        Returns:
            {
                'id': 'invite_id',
                'status': 'pending' | 'viewed' | 'signed' | 'declined',
                'created': timestamp,
                'updated': timestamp
            }
        """
        response = self._request(
            "GET",
            f"/v2/invites/{invite_id}"
        )
        
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SIGNING URL OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_signing_link(self, document_id, signer_email):
        """
        Generate embedded signing URL for a signer
        
        Args:
            document_id: SignNow document ID
            signer_email: Email of signer
        
        Returns:
            {
                'signing_link': 'https://...',
                'expires_at': timestamp
            }
        """
        payload = {
            "email": signer_email,
        }
        
        response = self._request(
            "POST",
            f"/v2/documents/{document_id}/signing-link",
            json=payload
        )
        
        data = response.json()
        logger.info(f"Generated signing link for {signer_email}")
        return data
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS POLLING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_document_status(self, document_id):
        """
        Poll document status from SignNow
        
        Returns normalized status with detailed signer info
        """
        doc = self.get_document_details(document_id)
        
        # Normalize status
        signnow_status = doc.get("status", "unknown")
        
        # Map SignNow status to our status
        status_map = {
            "pending": "sent",
            "viewed": "in_progress",
            "in_progress": "in_progress",
            "completed": "completed",
            "declined": "declined",
            "expired": "expired",
        }
        
        normalized_status = status_map.get(signnow_status, signnow_status)
        
        # Extract signer statuses from invitations
        signers_status = []
        for invite in doc.get("invites", []):
            signers_status.append({
                "email": invite.get("email"),
                "invite_id": invite.get("id"),
                "status": invite.get("status"),
                "signed_at": invite.get("signed_at"),
            })
        
        return {
            "document_id": document_id,
            "status": normalized_status,
            "signnow_status": signnow_status,
            "signers": signers_status,
            "is_completed": normalized_status == "completed",
            "updated_at": datetime.now().isoformat(),
        }
