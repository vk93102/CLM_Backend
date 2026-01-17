"""
Production-level Document Processing Services
Handles text extraction, chunking, embedding generation, and metadata extraction
"""
import re
import json
from typing import List, Dict, Optional, Tuple
from django.conf import settings
from authentication.r2_service import R2StorageService
from repository.embeddings_service import VoyageEmbeddingsService
import logging

logger = logging.getLogger(__name__)


class DocumentChunkingService:
    """Service for chunking documents into semantic segments"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize chunking service
        
        Args:
            chunk_size: Target words per chunk
            overlap: Overlap words between chunks for context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[Dict]:
        """
        Chunk text into segments with metadata
        
        Args:
            text: Full document text
        
        Returns:
            List of chunks with position info
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        start_char_index = 0
        
        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_word_count + word_count > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                end_char_index = start_char_index + len(chunk_text)
                
                chunks.append({
                    'text': chunk_text,
                    'start_char_index': start_char_index,
                    'end_char_index': end_char_index,
                    'word_count': current_word_count
                })
                
                # Handle overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 1 else current_chunk
                current_chunk = overlap_sentences
                current_word_count = sum(len(s.split()) for s in overlap_sentences)
                start_char_index = end_char_index - sum(len(s) + 1 for s in overlap_sentences)
            
            current_chunk.append(sentence)
            current_word_count += word_count
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            end_char_index = start_char_index + len(chunk_text)
            
            chunks.append({
                'text': chunk_text,
                'start_char_index': start_char_index,
                'end_char_index': end_char_index,
                'word_count': current_word_count
            })
        
        return chunks
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove extra whitespace and normalize text"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting on periods, exclamation, question marks
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


class TextExtractionService:
    """Service for extracting text from various file formats"""
    
    @staticmethod
    def extract_from_file(file_obj, file_type: str) -> Optional[str]:
        """
        Extract text from uploaded file
        
        Args:
            file_obj: Django UploadedFile object
            file_type: File extension (pdf, docx, txt, etc.)
        
        Returns:
            Extracted text or None if extraction failed
        """
        try:
            if file_type.lower() == 'txt':
                return TextExtractionService._extract_txt(file_obj)
            elif file_type.lower() == 'pdf':
                return TextExtractionService._extract_pdf(file_obj)
            elif file_type.lower() in ['docx', 'doc']:
                return TextExtractionService._extract_docx(file_obj)
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return None
        except Exception as e:
            logger.error(f"Text extraction error for {file_type}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_txt(file_obj) -> str:
        """Extract text from plain text file"""
        return file_obj.read().decode('utf-8', errors='ignore')
    
    @staticmethod
    def _extract_pdf(file_obj) -> Optional[str]:
        """Extract text from PDF"""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed. PDF extraction unavailable.")
            return None
    
    @staticmethod
    def _extract_docx(file_obj) -> Optional[str]:
        """Extract text from DOCX"""
        try:
            from docx import Document
            
            doc = Document(file_obj)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not installed. DOCX extraction unavailable.")
            return None


class PIIRedactionService:
    """Service for redacting personally identifiable information"""
    
    # Simple regex patterns for common PII
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }
    
    @classmethod
    def redact_pii(cls, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Redact PII from text
        
        Args:
            text: Text to redact
        
        Returns:
            Tuple of (redacted_text, redaction_counts)
        """
        redacted_text = text
        redaction_counts = {}
        
        for pii_type, pattern in cls.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                redaction_counts[pii_type] = len(matches)
                redacted_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", redacted_text)
        
        return redacted_text, redaction_counts


class MetadataExtractionService:
    """Service for extracting structured metadata from contracts using AI"""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
    
    def extract_metadata(self, text: str) -> Dict:
        """
        Extract structured metadata from contract text using Gemini API
        
        Args:
            text: Full contract text
        
        Returns:
            Dictionary with extracted metadata
        """
        if not self.gemini_api_key:
            logger.warning("No Gemini API key configured")
            return self._empty_metadata("No Gemini API key configured")
        
        try:
            # Use google-generativeai (older but stable SDK)
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            
            # Use gemini-2.0-flash model  
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Detailed prompt for metadata extraction
            prompt = f"""You are a legal contract analyzer. Extract structured metadata from this contract.

Return ONLY valid JSON with these exact fields (use null only if info not found):

{{
  "parties": ["list of party names, companies, organizations mentioned"],
  "contract_value": <numeric amount if found, null otherwise>,
  "currency": "<USD, EUR, GBP, etc or null>",
  "effective_date": "<YYYY-MM-DD or null>",
  "expiration_date": "<YYYY-MM-DD or null>",
  "identified_clauses": ["Confidentiality", "Termination", "Payment", "Liability", "Indemnity", "etc"],
  "summary": "<2-3 sentence summary of the agreement>",
  "risk_score": <0-100 number or null>
}}

CONTRACT TEXT:
{text}

EXTRACTION RULES:
- Extract ALL parties mentioned
- Extract numeric contract value (no currency symbols)
- Currency code only
- Use YYYY-MM-DD date format
- List all identified clause types
- Provide brief professional summary
- Risk score: 0=low, 50=medium, 100=high

Respond with ONLY valid JSON, no markdown, no code blocks."""
            
            response = model.generate_content(prompt)
            
            response_text = response.text.strip()
            
            # Clean any markdown
            for marker in ['```json', '```']:
                if response_text.startswith(marker):
                    response_text = response_text[len(marker):].lstrip()
                if response_text.endswith('```'):
                    response_text = response_text[:-3].rstrip()
            
            logger.info(f"Gemini response length: {len(response_text)}")
            
            # Parse JSON
            try:
                metadata = json.loads(response_text)
                
                # Ensure all fields present
                defaults = {
                    'parties': [],
                    'contract_value': None,
                    'currency': None,
                    'effective_date': None,
                    'expiration_date': None,
                    'identified_clauses': [],
                    'summary': '',
                    'risk_score': None
                }
                
                for field, default in defaults.items():
                    if field not in metadata:
                        metadata[field] = default
                
                logger.info(f"✓ Metadata extracted: {len([v for v in metadata.values() if v])} fields with values")
                return metadata
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}, response: {response_text[:200]}")
                return self._empty_metadata("JSON parsing failed")
        
        except Exception as e:
            logger.error(f"Metadata extraction failed: {type(e).__name__}: {str(e)}", exc_info=True)
            return self._empty_metadata(f"Error: {type(e).__name__}")
    
    def _empty_metadata(self, reason: str = "") -> Dict:
        """Return empty metadata structure"""
        return {
            'parties': [],
            'contract_value': None,
            'currency': None,
            'effective_date': None,
            'expiration_date': None,
            'identified_clauses': [],
            'summary': reason if reason else 'Unable to extract metadata',
            'risk_score': None
        }


class DocumentProcessingService:
    """Orchestrator service for complete document processing"""
    
    def __init__(self):
        self.chunking_service = DocumentChunkingService()
        self.text_extraction = TextExtractionService()
        self.pii_redaction = PIIRedactionService()
        self.metadata_extraction = MetadataExtractionService()
        self.embeddings_service = VoyageEmbeddingsService()
    
    def process_document(self, file_obj, document_model, r2_service: R2StorageService) -> Dict:
        """
        Complete document processing pipeline
        
        Args:
            file_obj: Uploaded file object
            document_model: Document model instance
            r2_service: R2 storage service
        
        Returns:
            Processing result with status, metadata, chunks, and embeddings
        """
        try:
            # Step 1: Extract text
            logger.info(f"Extracting text from {document_model.filename}")
            full_text = self.text_extraction.extract_from_file(file_obj, document_model.file_type)
            
            if not full_text:
                return {
                    'success': False,
                    'error': 'Failed to extract text from file'
                }
            
            # Step 2: Redact PII
            logger.info(f"Redacting PII from {document_model.filename}")
            redacted_text, redaction_counts = self.pii_redaction.redact_pii(full_text)
            
            # Step 3: Extract metadata
            logger.info(f"Extracting metadata from {document_model.filename}")
            metadata = self.metadata_extraction.extract_metadata(redacted_text[:3000])
            
            # Step 4: Create chunks
            logger.info(f"Creating chunks for {document_model.filename}")
            chunks = self.chunking_service.chunk_text(redacted_text)
            
            # Step 5: Generate embeddings for chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self._generate_chunk_embeddings(chunks)
            
            # Update document
            document_model.full_text = redacted_text
            document_model.extracted_metadata = {
                **metadata,
                'redaction_counts': redaction_counts,
                'chunk_count': len(chunks),
                'total_words': len(redacted_text.split()),
                'embeddings_generated': sum(1 for e in embeddings if e is not None)
            }
            document_model.status = 'processed'
            document_model.save()
            
            return {
                'success': True,
                'full_text': redacted_text,
                'metadata': metadata,
                'chunks': chunks,
                'embeddings': embeddings,
                'redaction_counts': redaction_counts,
                'chunk_count': len(chunks),
                'embeddings_count': sum(1 for e in embeddings if e is not None)
            }
        
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}", exc_info=True)
            document_model.status = 'failed'
            document_model.processing_error = str(e)
            document_model.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_chunk_embeddings(self, chunks: List[Dict]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for document chunks using Voyage AI
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
        
        Returns:
            List of embeddings (or None for failed items)
        """
        if not chunks:
            return []
        
        # Extract chunk texts
        chunk_texts = [chunk.get('text', '') for chunk in chunks]
        
        # Generate embeddings
        if self.embeddings_service.is_available():
            logger.info(f"Using Voyage AI to generate embeddings for {len(chunk_texts)} chunks")
            embeddings = self.embeddings_service.embed_batch(chunk_texts)
        else:
            logger.warning("Voyage AI not available, embeddings will be None")
            embeddings = [None] * len(chunk_texts)
        
        return embeddings
