"""
Celery tasks for AI operations
Draft generation using RAG + Gemini with citation tracking
"""
import logging
from celery import shared_task
from django.utils import timezone
from ai.models import DraftGenerationTask
from repository.models import DocumentChunk, Document
from repository.embeddings_service import VoyageEmbeddingsService
from contracts.models import ContractTemplate
import google.generativeai as genai
from django.conf import settings
import numpy as np
import json

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


@shared_task(bind=True, max_retries=3)
def generate_draft_async(self, task_id: str, tenant_id: str, contract_type: str, 
                        input_params: dict, template_id: str = None):
    """
    Async task to generate contract draft using RAG + Gemini
    
    Workflow:
    1. Retrieve template if specified
    2. Build RAG context from similar clauses in tenant's repository
    3. Generate draft with Gemini using template + RAG context
    4. Track source clause citations
    5. Update task record with results
    
    Args:
        task_id: UUID of DraftGenerationTask
        tenant_id: Tenant UUID for isolation
        contract_type: Type of contract to generate (NDA, MSA, etc.)
        input_params: Dictionary with generation parameters (parties, value, dates, etc.)
        template_id: Optional template UUID to use as base
    
    Returns:
        dict: Status, task_id, generated_length, and citations_count
    """
    try:
        # Update task status
        task = DraftGenerationTask.objects.get(id=task_id, tenant_id=tenant_id)
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        logger.info(f"Starting draft generation for task {task_id}, type: {contract_type}")
        
        # Step 1: Retrieve template if specified
        template_text = ""
        template_info = ""
        if template_id:
            try:
                template = ContractTemplate.objects.get(id=template_id, tenant_id=tenant_id)
                # Note: ContractTemplate stores r2_key, not full text
                # You may need to retrieve from R2 or implement a text field
                template_info = f"Template: {template.name} (v{template.version})"
                logger.info(f"Using template: {template_info}")
            except ContractTemplate.DoesNotExist:
                logger.warning(f"Template {template_id} not found, proceeding without template")
            except Exception as e:
                logger.warning(f"Error retrieving template: {e}")
        
        # Step 2: Build RAG context from similar clauses
        context_clauses = []
        citations = []
        
        # Generate embedding for the contract type + parameters
        search_query = f"{contract_type} "
        for key, value in input_params.items():
            if isinstance(value, (str, int, float)):
                search_query += f"{key}: {value} "
        
        embeddings_service = VoyageEmbeddingsService()
        
        try:
            query_embedding = embeddings_service.embed_query(search_query)
            
            if query_embedding:
                # Find similar document chunks from tenant's repository
                chunks = DocumentChunk.objects.filter(
                    document__tenant_id=tenant_id,
                    embedding__isnull=False,
                    is_processed=True
                ).select_related('document')[:100]  # Limit to recent chunks
                
                if chunks.exists():
                    # Calculate similarities using cosine distance
                    query_vec = np.array(query_embedding, dtype=np.float32)
                    query_norm = np.linalg.norm(query_vec)
                    
                    chunk_scores = []
                    for chunk in chunks:
                        try:
                            if not chunk.embedding:
                                continue
                            
                            chunk_vec = np.array(chunk.embedding, dtype=np.float32)
                            chunk_norm = np.linalg.norm(chunk_vec)
                            
                            if chunk_norm > 0 and query_norm > 0:
                                # Cosine similarity
                                similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
                                
                                if similarity > 0.3:  # Relevance threshold
                                    chunk_scores.append({
                                        'chunk': chunk,
                                        'similarity': float(similarity)
                                    })
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error calculating similarity for chunk {chunk.id}: {e}")
                            continue
                    
                    # Sort by similarity and take top 5
                    chunk_scores.sort(key=lambda x: x['similarity'], reverse=True)
                    for item in chunk_scores[:5]:
                        chunk = item['chunk']
                        context_clauses.append({
                            'text': chunk.text,
                            'chunk_id': str(chunk.id),
                            'document_id': str(chunk.document_id),
                            'filename': chunk.document.filename,
                            'similarity': item['similarity']
                        })
                        citations.append({
                            'chunk_id': str(chunk.id),
                            'document_id': str(chunk.document_id),
                            'filename': chunk.document.filename,
                            'chunk_number': chunk.chunk_number,
                            'similarity_score': item['similarity']
                        })
                    
                    logger.info(f"Found {len(context_clauses)} relevant clauses for RAG context")
                else:
                    logger.info("No document chunks found in repository for RAG context")
        
        except Exception as e:
            logger.warning(f"RAG context building failed: {e}")
        
        # Step 3: Generate draft with Gemini
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Build comprehensive prompt
            prompt_parts = [
                f"You are a professional legal AI assistant specializing in contract drafting.",
                f"\n\nCONTRACT TYPE: {contract_type}",
            ]
            
            # Add template info if available
            if template_info:
                prompt_parts.append(f"\nREFERENCE TEMPLATE: {template_info}")
            
            # Add input parameters
            if input_params:
                prompt_parts.append("\nCONTRACT PARAMETERS:")
                for key, value in input_params.items():
                    prompt_parts.append(f"  - {key}: {value}")
            
            # Add RAG context
            if context_clauses:
                prompt_parts.append("\nRELEVANT CLAUSES FROM SIMILAR CONTRACTS:")
                for i, item in enumerate(context_clauses, 1):
                    prompt_parts.append(f"\n[Clause {i} from {item['filename']} - Similarity: {item['similarity']:.2%}]")
                    prompt_parts.append(item['text'][:800])  # Limit context length
            
            # Add generation instructions
            prompt_parts.extend([
                "\nINSTRUCTIONS:",
                "1. Generate a comprehensive, professional contract draft",
                "2. Include all standard sections appropriate for this contract type:",
                "   - Title and Effective Date",
                "   - Parties and Roles",
                "   - Definitions",
                "   - Scope of Work / Products",
                "   - Obligations and Responsibilities",
                "   - Payment Terms",
                "   - Term and Termination",
                "   - Confidentiality",
                "   - Limitation of Liability",
                "   - Dispute Resolution",
                "   - Governing Law",
                "   - General Provisions",
                "3. Use professional legal language",
                "4. Ensure all parameters are incorporated",
                "5. Use relevant clauses from context where appropriate",
            ])
            
            prompt = "\n".join(prompt_parts)
            
            logger.info(f"Generating draft via Gemini (prompt length: {len(prompt)} chars)")
            
            response = model.generate_content(prompt)
            generated_text = response.text
            
            logger.info(f"Draft generation complete: {len(generated_text)} characters")
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
        
        # Step 4: Update task with results
        task.status = 'completed'
        task.generated_text = generated_text
        task.citations = citations
        task.completed_at = timezone.now()
        task.save()
        
        logger.info(f"Task {task_id} completed successfully ({len(generated_text)} chars, {len(citations)} citations)")
        
        return {
            'status': 'completed',
            'task_id': str(task_id),
            'generated_length': len(generated_text),
            'citations_count': len(citations)
        }
    
    except DraftGenerationTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {
            'status': 'failed',
            'task_id': str(task_id),
            'error': 'Task not found'
        }
    
    except Exception as e:
        logger.error(f"Draft generation failed for task {task_id}: {str(e)}", exc_info=True)
        
        # Update task with error status
        try:
            task = DraftGenerationTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)[:1000]  # Truncate to reasonable length
            task.completed_at = timezone.now()
            task.save()
        except Exception as update_error:
            logger.error(f"Failed to update task status: {update_error}")
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
            logger.info(f"Retrying task in {countdown}s (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=countdown)
        
        return {
            'status': 'failed',
            'task_id': str(task_id),
            'error': str(e)
        }
