"""
PII (Personally Identifiable Information) Scrubbing Service

This module provides utilities to detect and redact PII before API calls to Gemini, Voyage AI.
Catches: email, phone, SSN, credit card, passport, driver license, bank account, IP addresses, etc.
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PiiEntity:
    """Represents a detected PII entity"""
    entity_type: str  # email, phone, ssn, credit_card, etc.
    value: str  # Original value
    redacted: str  # Redacted version
    confidence: float  # 0.0-1.0
    start_pos: int  # Position in text
    end_pos: int  # End position in text


class PIIScrubber:
    """Main PII scrubbing service"""
    
    # PII Patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone_us': r'\b(\+1)?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'phone_international': r'\+(?:[0-9] ?){6,14}[0-9]',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',  # XXX-XX-XXXX
        'ssn_no_dash': r'\b\d{9}\b(?<!\d)',  # 9 consecutive digits
        'credit_card': r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
        'amex': r'\b3[47]\d{13}\b',
        'visa': r'\b4\d{12}(?:\d{3})?\b',
        'mastercard': r'\b5[1-5]\d{14}\b',
        'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
        'driver_license': r'\b[A-Z]{1,2}\d{5,8}\b',
        'bank_account': r'\b\d{8,17}\b',  # Variable length account numbers
        'ipv4': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'ipv6': r'(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}',
        'medical_record': r'\bMRN[:\s]+([A-Z0-9\-]+)\b',
        'vin': r'\b[A-HJ-NPR-Z0-9]{17}\b',  # Vehicle Identification Number
        'api_key': r'\b(?:api[_-]?key|apikey|api_token)[:\s=]+([A-Za-z0-9\-_.]{20,})\b',
        'jwt': r'\beyJ[A-Za-z0-9\-_.]+\.[A-Za-z0-9\-_.]+\.[A-Za-z0-9\-_.]*\b',
        'aws_secret': r'\bAWS[_A-Z]{0,30}[:\s=]+([A-Za-z0-9/+=]{40})\b',
    }
    
    # Common PII keywords to flag context
    PII_KEYWORDS = [
        'address', 'apartment', 'street', 'city', 'state', 'zipcode', 'zip',
        'date of birth', 'dob', 'birth date', 'ssn', 'social security',
        'credit card', 'cvv', 'cvc', 'card number', 'expiration',
        'bank account', 'routing number', 'account number',
        'passport', 'visa', 'driver license', 'license',
        'email', 'phone', 'mobile', 'telephone',
        'ip address', 'ip', 'ipv4', 'ipv6',
        'api key', 'secret', 'token', 'password',
        'medical', 'health', 'insurance', 'claim',
    ]
    
    def __init__(self, redaction_char: str = '*', min_confidence: float = 0.6):
        """
        Initialize PII Scrubber
        
        Args:
            redaction_char: Character to use for redaction (default: *)
            min_confidence: Minimum confidence threshold to consider PII (0.0-1.0)
        """
        self.redaction_char = redaction_char
        self.min_confidence = min_confidence
        self.compiled_patterns = {
            key: re.compile(pattern, re.IGNORECASE)
            for key, pattern in self.PII_PATTERNS.items()
        }
    
    def scrub_text(self, text: str, return_details: bool = False) -> Union[str, Tuple[str, List[PiiEntity]]]:
        """
        Scrub PII from text
        
        Args:
            text: Text to scrub
            return_details: If True, return tuple of (scrubbed_text, pii_entities)
        
        Returns:
            Scrubbed text or tuple with details
        """
        if not text:
            return text if not return_details else (text, [])
        
        pii_entities: List[PiiEntity] = []
        scrubbed_text = text
        offset = 0  # Track position changes due to replacements
        
        # Detect PII entities
        for entity_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                confidence = self._calculate_confidence(entity_type, value)
                
                if confidence >= self.min_confidence:
                    redacted = self._redact_value(value, entity_type)
                    entity = PiiEntity(
                        entity_type=entity_type,
                        value=value,
                        redacted=redacted,
                        confidence=confidence,
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    pii_entities.append(entity)
        
        # Sort by position (reverse) to avoid position shifts
        pii_entities.sort(key=lambda e: e.start_pos, reverse=True)
        
        # Replace PII in text
        for entity in pii_entities:
            scrubbed_text = (
                scrubbed_text[:entity.start_pos] + 
                entity.redacted + 
                scrubbed_text[entity.end_pos:]
            )
        
        if return_details:
            return scrubbed_text, pii_entities
        return scrubbed_text
    
    def scrub_dict(self, data: dict, return_details: bool = False) -> Union[dict, Tuple[dict, Dict]]:
        """
        Scrub PII from dictionary values
        
        Args:
            data: Dictionary to scrub
            return_details: If True, return tuple with PII details
        
        Returns:
            Scrubbed dictionary or tuple with details
        """
        scrubbed_data = {}
        all_pii_entities = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                if return_details:
                    scrubbed_value, entities = self.scrub_text(value, return_details=True)
                    scrubbed_data[key] = scrubbed_value
                    if entities:
                        all_pii_entities[key] = entities
                else:
                    scrubbed_data[key] = self.scrub_text(value)
            elif isinstance(value, dict):
                if return_details:
                    scrubbed_value, entities = self.scrub_dict(value, return_details=True)
                    scrubbed_data[key] = scrubbed_value
                    if entities:
                        all_pii_entities[key] = entities
                else:
                    scrubbed_data[key] = self.scrub_dict(value)
            elif isinstance(value, list):
                if return_details:
                    scrubbed_list, entities = self.scrub_list(value, return_details=True)
                    scrubbed_data[key] = scrubbed_list
                    if entities:
                        all_pii_entities[key] = entities
                else:
                    scrubbed_data[key] = self.scrub_list(value)
            else:
                scrubbed_data[key] = value
        
        if return_details:
            return scrubbed_data, all_pii_entities
        return scrubbed_data
    
    def scrub_list(self, data: list, return_details: bool = False) -> Union[list, Tuple[list, Dict]]:
        """Scrub PII from list items"""
        scrubbed_list = []
        all_pii_entities = {}
        
        for i, item in enumerate(data):
            if isinstance(item, str):
                if return_details:
                    scrubbed_item, entities = self.scrub_text(item, return_details=True)
                    scrubbed_list.append(scrubbed_item)
                    if entities:
                        all_pii_entities[f"[{i}]"] = entities
                else:
                    scrubbed_list.append(self.scrub_text(item))
            elif isinstance(item, dict):
                if return_details:
                    scrubbed_item, entities = self.scrub_dict(item, return_details=True)
                    scrubbed_list.append(scrubbed_item)
                    if entities:
                        all_pii_entities[f"[{i}]"] = entities
                else:
                    scrubbed_list.append(self.scrub_dict(item))
            else:
                scrubbed_list.append(item)
        
        if return_details:
            return scrubbed_list, all_pii_entities
        return scrubbed_list
    
    def _calculate_confidence(self, entity_type: str, value: str) -> float:
        """Calculate confidence score for PII detection"""
        confidence_scores = {
            'email': 0.95,
            'phone_us': 0.90,
            'phone_international': 0.85,
            'ssn': 0.99,
            'ssn_no_dash': 0.75,  # Lower confidence (could be other numbers)
            'credit_card': 0.95,
            'amex': 0.98,
            'visa': 0.98,
            'mastercard': 0.98,
            'passport': 0.85,
            'driver_license': 0.80,
            'bank_account': 0.70,  # Lower confidence (could be other numbers)
            'ipv4': 0.90,
            'ipv6': 0.95,
            'medical_record': 0.92,
            'vin': 0.90,
            'api_key': 0.95,
            'jwt': 0.98,
            'aws_secret': 0.99,
        }
        return confidence_scores.get(entity_type, 0.5)
    
    def _redact_value(self, value: str, entity_type: str) -> str:
        """Redact a value based on type"""
        # Keep some context for readability
        if entity_type == 'email':
            # Keep email domain visible but redact local part
            parts = value.split('@')
            return f"{self.redaction_char * max(1, len(parts[0]) - 2)}{parts[0][-2:]}@{parts[1]}"
        
        elif entity_type in ['phone_us', 'phone_international']:
            # Show last 4 digits
            return f"+{'1' if '+1' in value else ''}({self.redaction_char * 3}){self.redaction_char * 3}-{value[-4:]}"
        
        elif entity_type in ['ssn', 'ssn_no_dash']:
            # Show last 4 digits
            digits = re.sub(r'\D', '', value)
            return f"{'*' * 5}-{'*' * 2}-{digits[-4:]}"
        
        elif entity_type in ['credit_card', 'amex', 'visa', 'mastercard']:
            # Show last 4 digits
            digits = re.sub(r'\D', '', value)
            return f"{self.redaction_char * 12}{digits[-4:]}"
        
        elif entity_type in ['passport', 'driver_license', 'vin']:
            # Show first 2 chars, redact rest
            return f"{value[:2]}{self.redaction_char * (len(value) - 2)}"
        
        elif entity_type == 'bank_account':
            # Show last 4 digits
            return f"{self.redaction_char * max(1, len(value) - 4)}{value[-4:]}"
        
        elif entity_type in ['ipv4', 'ipv6']:
            return "[REDACTED_IP]"
        
        elif entity_type in ['api_key', 'jwt', 'aws_secret']:
            return f"[REDACTED_{entity_type.upper()}]"
        
        else:
            # Default: redact entire value
            return self.redaction_char * len(value)
    
    def log_pii_detection(self, pii_entities: List[PiiEntity], context: Dict = None) -> None:
        """
        Log detected PII for audit purposes
        
        Args:
            pii_entities: List of detected PII entities
            context: Additional context (user_id, tenant_id, endpoint, etc.)
        """
        if not pii_entities:
            return
        
        context = context or {}
        
        for entity in pii_entities:
            log_entry = {
                'event': 'PII_DETECTED_AND_REDACTED',
                'entity_type': entity.entity_type,
                'confidence': entity.confidence,
                'redacted_value': entity.redacted,
                'timestamp': self._get_timestamp(),
                **context
            }
            
            logger.warning(
                f"PII Detection: {entity.entity_type} (confidence: {entity.confidence}) "
                f"User: {context.get('user_id')}, Tenant: {context.get('tenant_id')}"
            )
            logger.info(f"PII Redaction Log: {json.dumps(log_entry)}")
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current ISO timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def validate_scrubbing(self, original: str, scrubbed: str) -> Dict:
        """
        Validate that scrubbing was effective
        
        Returns:
            {
                'original_pii_count': int,
                'scrubbed_pii_count': int,
                'effectiveness': float (0.0-1.0),
                'remaining_risks': [str]
            }
        """
        _, original_pii = self.scrub_text(original, return_details=True)
        _, scrubbed_pii = self.scrub_text(scrubbed, return_details=True)
        
        original_count = len(original_pii)
        scrubbed_count = len(scrubbed_pii)
        
        effectiveness = 1.0 - (scrubbed_count / max(1, original_count))
        
        remaining_risks = [f"{e.entity_type} (confidence: {e.confidence})" for e in scrubbed_pii]
        
        return {
            'original_pii_count': original_count,
            'scrubbed_pii_count': scrubbed_count,
            'effectiveness': effectiveness,
            'remaining_risks': remaining_risks
        }


# Singleton instance
_pii_scrubber = None


def get_pii_scrubber() -> PIIScrubber:
    """Get singleton PII scrubber instance"""
    global _pii_scrubber
    if _pii_scrubber is None:
        _pii_scrubber = PIIScrubber()
    return _pii_scrubber
