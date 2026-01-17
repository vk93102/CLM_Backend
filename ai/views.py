from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AIInferenceModel, DraftGenerationTask, ClauseAnchor
from .serializers import (
    AIInferenceSerializer,
    DraftGenerationTaskSerializer,
    ClauseAnchorSerializer,
    MetadataExtractionSerializer,
    ClauseClassificationSerializer
)
from .tasks import generate_draft_async
from django.utils import timezone
from django.db.models import Q
import uuid
import logging
import json
from repository.models import Document, DocumentChunk
from repository.embeddings_service import VoyageEmbeddingsService
import google.generativeai as genai
from django.conf import settings
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class AIViewSet(viewsets.ViewSet):
    """
    AI Endpoints for:
    - Endpoint 3: Draft Generation (Async) with RAG + Citation Tracking
    - Endpoint 4: Metadata Extraction from contracts
    - Endpoint 5: Clause Classification using semantic similarity
    """
    permission_classes = [IsAuthenticated]

    # ==========================================
    # ENDPOINT 3: DRAFT GENERATION (ASYNC)
    # ==========================================

    @action(detail=False, methods=['post'], url_path='generate/draft')
    def generate_draft(self, request):
        """
        Endpoint 3: Draft Generation (Async)
        POST /api/v1/ai/generate/draft/
        
        Request Body:
        {
            "contract_type": "NDA|MSA|Service Agreement|etc",
            "input_params": {
                "parties": ["Party A", "Party B"],
                "contract_value": 50000,
                "start_date": "2024-01-01",
                "end_date": "2025-01-01",
                "...other parameters..."
            },
            "template_id": "optional-uuid"
        }
        
        Response (202 Accepted):
        {
            "id": "task-uuid",
            "task_id": "celery-task-id",
            "status": "pending",
            "contract_type": "NDA",
            "created_at": "2024-01-17T...",
            "...full task details..."
        }
        """
        try:
            contract_type = request.data.get('contract_type', '').strip()
            input_params = request.data.get('input_params', {})
            template_id = request.data.get('template_id')

            # Validation
            if not contract_type:
                return Response(
                    {'error': 'contract_type is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(input_params, dict):
                return Response(
                    {'error': 'input_params must be a dictionary'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create task record in DB
            task = DraftGenerationTask.objects.create(
                tenant_id=request.user.tenant_id,
                user_id=request.user.user_id,
                contract_type=contract_type,
                input_params=input_params,
                template_id=template_id,
                task_id=str(uuid.uuid4()),  # Temporary, will be updated
                status='pending'
            )

            # Queue async Celery task
            celery_task = generate_draft_async.delay(
                task_id=str(task.id),
                tenant_id=str(request.user.tenant_id),
                contract_type=contract_type,
                input_params=input_params,
                template_id=str(template_id) if template_id else None
            )
            
            # Update task with actual Celery task ID
            task.task_id = celery_task.id
            task.save()

            serializer = DraftGenerationTaskSerializer(task)
            logger.info(f"Draft generation task created: {task.id}, celery task: {celery_task.id}")
            
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Error creating draft generation task: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to create generation task', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='generate/status/(?P<task_id>[^/.]+)')
    def get_draft_status(self, request, task_id=None):
        """
        GET /api/v1/ai/generate/status/{task_id}/
        
        Response:
        {
            "id": "task-uuid",
            "task_id": "celery-task-id",
            "status": "pending|processing|completed|failed",
            "contract_type": "NDA",
            "generated_text": "...draft content...",
            "citations": [
                {
                    "chunk_id": "uuid",
                    "document_id": "uuid",
                    "filename": "reference.pdf",
                    "similarity_score": 0.85
                }
            ],
            "error_message": null,
            "started_at": "2024-01-17T...",
            "completed_at": "2024-01-17T...",
            "created_at": "2024-01-17T...",
            "updated_at": "2024-01-17T..."
        }
        """
        try:
            # Look up by task_id (could be DB id or Celery task ID)
            task = DraftGenerationTask.objects.filter(
                Q(task_id=task_id) | Q(id=task_id),
                tenant_id=request.user.tenant_id
            ).first()
            
            if not task:
                logger.warning(f"Task not found: {task_id} for tenant {request.user.tenant_id}")
                return Response(
                    {'error': 'Task not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = DraftGenerationTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching task status: {e}")
            return Response(
                {'error': 'Failed to fetch task status', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==========================================
    # ENDPOINT 4: METADATA EXTRACTION
    # ==========================================

    @action(detail=False, methods=['post'], url_path='extract/metadata')
    def extract_metadata(self, request):
        """
        Endpoint 4: Metadata Extraction
        POST /api/v1/ai/extract/metadata/
        
        Request Body:
        {
            "document_id": "uuid"
        }
        
        Response (200 OK):
        {
            "parties": [
                {
                    "name": "Company A Inc.",
                    "role": "Licensor"
                },
                {
                    "name": "Company B LLC",
                    "role": "Licensee"
                }
            ],
            "effective_date": "2024-01-01",
            "termination_date": "2025-01-01",
            "contract_value": {
                "amount": 50000,
                "currency": "USD"
            }
        }
        """
        try:
            document_id = request.data.get('document_id')
            document_text = request.data.get('document_text')  # For testing
            
            if not document_id and not document_text:
                return Response(
                    {'error': 'Either document_id or document_text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch document with tenant isolation OR use provided text
            if document_text:
                # Use provided text directly (for testing)
                full_text = document_text
                logger.info("Using provided document_text for extraction")
            else:
                # Fetch from database
                try:
                    document = Document.objects.get(
                        id=document_id,
                        tenant_id=request.user.tenant_id
                    )
                except Document.DoesNotExist:
                    logger.warning(f"Document not found: {document_id}")
                    return Response(
                        {'error': 'Document not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Validate document has text content
                if not document.full_text or len(document.full_text.strip()) == 0:
                    logger.warning(f"Document has no full_text: {document_id}")
                    return Response(
                        {'error': 'Document has no text content. Please ensure OCR/text extraction is complete.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                full_text = document.full_text

            # Call Gemini with structured prompt (using genai library)
            # Note: Using Gemini 2.0 Flash as primary model for optimal performance
            logger.info(f"Extracting metadata using Gemini 2.0 Flash for document: {document_id}")
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as model_error:
                logger.warning(f"Gemini 2.0 Flash not available: {model_error}, trying fallback models")
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                except Exception:
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                    except Exception:
                        model = genai.GenerativeModel('gemini-pro')
            
            # Prepare JSON schema for extraction
            extraction_schema = {
                "parties": [
                    {"name": "string", "role": "string (e.g., 'Licensor', 'Licensee', 'Buyer', 'Seller')"}
                ],
                "effective_date": "YYYY-MM-DD or null",
                "termination_date": "YYYY-MM-DD or null",
                "contract_value": {
                    "amount": "number or null",
                    "currency": "ISO 4217 code (USD, EUR, GBP, etc.) or null"
                }
            }
            
            prompt = f"""Extract structured metadata from this contract.

IMPORTANT: Return ONLY valid JSON matching this schema exactly:
{json.dumps(extraction_schema, indent=2)}

EXTRACTION RULES:
1. Parties: Extract all parties mentioned in the contract header/signature section with their roles
2. Dates: Look for "Effective Date", "Commencement Date", "Term ends", "Expiration Date", "Termination Date"
3. Value: Look for contract value/consideration amount. Include only numeric value (no currency symbols)
4. Currency: Use ISO 4217 currency codes
5. If a field is not found or unclear, use null

Contract Text (first 10,000 characters):
---
{full_text[:10000]}
---

Return ONLY the JSON object, no other text."""

            logger.info(f"Extracting metadata from document: {document_id}")
            try:
                response = model.generate_content(prompt)
                
                # Parse and validate response
                try:
                    response_text = response.text.strip()
                    
                    # Clean up markdown code blocks if present
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.startswith('```'):
                        response_text = response_text[3:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    
                    response_text = response_text.strip()
                    
                    extracted_data = json.loads(response_text)
                    
                    # Validate structure
                    if not isinstance(extracted_data, dict):
                        raise ValueError("Response is not a JSON object")
                    
                    # Ensure required keys exist
                    required_keys = ['parties', 'effective_date', 'termination_date', 'contract_value']
                    for key in required_keys:
                        if key not in extracted_data:
                            extracted_data[key] = None
                    
                    # Validate contract_value structure
                    if extracted_data.get('contract_value') and isinstance(extracted_data['contract_value'], dict):
                        if 'amount' not in extracted_data['contract_value']:
                            extracted_data['contract_value']['amount'] = None
                        if 'currency' not in extracted_data['contract_value']:
                            extracted_data['contract_value']['currency'] = None
                    
                    logger.info(f"Metadata extraction successful for document {document_id}")
                    return Response(extracted_data, status=status.HTTP_200_OK)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini JSON response: {e}")
                    # Fallback: return basic extraction
                    return Response({
                        "parties": [],
                        "effective_date": None,
                        "termination_date": None,
                        "contract_value": {"amount": None, "currency": None},
                        "message": "Fallback response due to API unavailability"
                    }, status=status.HTTP_200_OK)
            except Exception as gemini_error:
                logger.warning(f"Gemini API error, using fallback extraction: {gemini_error}")
                # Fallback metadata extraction using simple string matching
                import re
                
                extracted_data = {
                    "parties": [],
                    "effective_date": None,
                    "termination_date": None,
                    "contract_value": {"amount": None, "currency": "USD"}
                }
                
                # Extract parties (names with Inc, LLC, Corp, etc.)
                party_pattern = r'([A-Za-z&\s\.]+(?:Inc|LLC|Corp|Ltd|Company|Corporation|Partnership|LLP))'
                parties = re.findall(party_pattern, full_text)
                if parties:
                    extracted_data["parties"] = [{"name": p.strip(), "role": None} for p in parties[:5]]
                
                # Extract dates (YYYY-MM-DD format)
                date_pattern = r'(\d{4}-\d{2}-\d{2})'
                dates = re.findall(date_pattern, full_text)
                if dates:
                    extracted_data["effective_date"] = dates[0]
                    if len(dates) > 1:
                        extracted_data["termination_date"] = dates[-1]
                
                # Extract currency amounts
                amount_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
                amounts = re.findall(amount_pattern, full_text)
                if amounts:
                    # Remove commas and convert to float
                    amount_str = amounts[0].replace(',', '')
                    extracted_data["contract_value"]["amount"] = float(amount_str)
                
                logger.info(f"Fallback metadata extraction for document {document_id}")
                return Response(extracted_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Metadata extraction error: {e}", exc_info=True)
            return Response(
                {'error': 'Metadata extraction failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==========================================
    # ENDPOINT 5: CLAUSE CLASSIFICATION
    # ==========================================

    @action(detail=False, methods=['post'], url_path='classify')
    def classify_clause(self, request):
        """
        Endpoint 5: Clause Classification
        POST /api/v1/ai/classify/
        
        Classifies input text by finding the nearest anchor clause using cosine similarity.
        Pre-populated anchor clauses: Indemnity, Termination, Confidentiality, Liability, etc.
        
        Request Body:
        {
            "text": "The parties agree to keep all information confidential..."
        }
        
        Response (200 OK):
        {
            "label": "Confidentiality",
            "category": "Legal",
            "confidence": 0.92
        }
        """
        try:
            text = request.data.get('text', '').strip()
            
            if not text:
                return Response(
                    {'error': 'text is required and cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(text) < 20:
                return Response(
                    {'error': 'text must be at least 20 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get all active anchor clauses with embeddings
            anchors = ClauseAnchor.objects.filter(
                is_active=True
            ).exclude(embedding__isnull=True)
            
            if not anchors.exists():
                logger.error("No active anchor clauses found")
                return Response(
                    {'error': 'No anchor clauses configured. System initialization required.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Generate embedding for input text
            embeddings_service = VoyageEmbeddingsService()
            query_embedding = embeddings_service.embed_query(text)

            if not query_embedding:
                logger.error("Failed to generate embedding for input text")
                return Response(
                    {'error': 'Failed to generate text embedding'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Calculate cosine similarity with all anchors
            query_vec = np.array(query_embedding, dtype=np.float32)
            query_norm = np.linalg.norm(query_vec)
            
            if query_norm == 0:
                logger.error("Query embedding has zero norm")
                return Response(
                    {'error': 'Invalid text embedding'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            scores = []
            for anchor in anchors:
                try:
                    if not anchor.embedding:
                        continue
                    
                    anchor_vec = np.array(anchor.embedding, dtype=np.float32)
                    anchor_norm = np.linalg.norm(anchor_vec)
                    
                    if anchor_norm > 0:
                        # Cosine similarity: (A·B) / (||A|| * ||B||)
                        similarity = np.dot(query_vec, anchor_vec) / (query_norm * anchor_norm)
                        
                        scores.append({
                            'label': anchor.label,
                            'category': anchor.category,
                            'confidence': float(max(0, min(1, (similarity + 1) / 2)))  # Normalize to 0-1
                        })
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing anchor {anchor.id}: {e}")
                    continue

            if not scores:
                logger.error("No valid anchor scores calculated")
                return Response(
                    {'error': 'Could not classify clause'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Find nearest anchor by confidence (cosine similarity)
            best_match = max(scores, key=lambda x: x['confidence'])
            
            logger.info(f"Classified text as '{best_match['label']}' (confidence: {best_match['confidence']:.2%})")
            
            return Response(best_match, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Clause classification error: {e}", exc_info=True)
            return Response(
                {'error': 'Classification failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

