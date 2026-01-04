"""
NER (Named Entity Recognition) service
Hybrid approach: Rule-based extraction (primary) + spaCy NER (fallback)
Optimized for certificate documents with non-standard text layouts
"""
import re
from typing import Dict, Optional, List, Tuple
import spacy

from utils import get_logger
from database.models import ExtractedEntities


logger = get_logger("ner_service")


class CertificateTextPreprocessor:
    """Preprocesses OCR text for certificate entity extraction"""
    
    @staticmethod
    def preprocess(text: str) -> str:
        """
        Preprocess OCR text for better entity extraction
        
        Args:
            text: Raw OCR text from certificate
            
        Returns:
            Normalized text with preserved line structure
        """
        if not text:
            return ""
        
        # Normalize whitespace within lines
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Strip leading/trailing spaces
            line = line.strip()
            # Skip empty lines
            if line:
                # Normalize multiple spaces to single space
                line = re.sub(r'\s+', ' ', line)
                normalized_lines.append(line)
        
        # Join back preserving line structure
        return '\n'.join(normalized_lines)
    
    @staticmethod
    def get_lines(text: str) -> List[str]:
        """Get cleaned lines from text"""
        return [line.strip() for line in text.split('\n') if line.strip()]


class RuleBasedEntityExtractor:
    """Rule-based entity extraction optimized for certificates"""
    
    PERSON_NAME_TRIGGERS = [
        "certify that", "this is to certify", "presented to",
        "awarded to", "certificate awarded", "issued to",
        "in recognition of", "to certify that"
    ]
    
    ORGANIZATION_TRIGGERS = [
        "issued by", "offered by", "authorized by", "by",
        "conducted by", "presented by", "from"
    ]
    
    ORGANIZATION_KEYWORDS = [
        "coursera", "edx", "udemy", "pluralsight", "linkedin",
        "university", "institute", "college", "academy", "school",
        "company", "corporation", "organization"
    ]
    
    DATE_TRIGGERS = [
        "date", "issued on", "issue date", "on",
        "dated", "completion date", "awarded on"
    ]
    
    CERTIFICATE_KEYWORDS = [
        "certificate", "completion", "achievement", "recognition",
        "course", "program", "specialization", "credential"
    ]
    
    @classmethod
    def extract_person_name(
        cls,
        lines: List[str],
        certificate_title_idx: Optional[int],
        used_indices: set
    ) -> Tuple[Optional[str], str]:
        """Extract person name using strict positional and validation rules"""
        # Ensure we never reuse the certificate title line or previously used lines
        blocked = used_indices.union({certificate_title_idx} if certificate_title_idx is not None else set())

        # Rule: must appear after trigger phrases, on the next meaningful line
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(trigger in line_lower for trigger in cls.PERSON_NAME_TRIGGERS):
                # Look at the next non-blocked line
                j = i + 1
                while j < len(lines) and j in blocked:
                    j += 1
                if j < len(lines):
                    candidate = lines[j].strip()
                    if cls._is_valid_name(candidate):
                        used_indices.add(j)
                        logger.info("Person name extracted via rule-based (after trigger)")
                        return candidate, "rule_based"

        # Fallback within rules: title-case line not blocked and not all caps
        for idx, line in enumerate(lines):
            if idx in blocked:
                continue
            if cls._is_valid_name(line):
                used_indices.add(idx)
                logger.info("Person name extracted via fallback line analysis")
                return line, "rule_based"

        return None, "not_found"
    
    @classmethod
    def extract_organization(
        cls,
        lines: List[str],
        used_indices: set,
        certificate_title_idx: Optional[int]
    ) -> Tuple[Optional[str], str]:
        """Extract organization only after allowed triggers"""
        blocked = used_indices.union({certificate_title_idx} if certificate_title_idx is not None else set())

        for i, line in enumerate(lines):
            if i in blocked:
                continue
            line_lower = line.lower()
            if any(trigger in line_lower for trigger in cls.ORGANIZATION_TRIGGERS):
                # Organization expected on same line after delimiter or next line
                # First try same line (text after trigger)
                for trigger in cls.ORGANIZATION_TRIGGERS:
                    if trigger in line_lower:
                        # capture text after trigger
                        pattern = rf"{trigger}\s*[:\-]?\s*(.+)"
                        m = re.search(pattern, line, flags=re.IGNORECASE)
                        if m:
                            candidate = m.group(1).strip()
                            if cls._is_valid_organization(candidate):
                                used_indices.add(i)
                                logger.info("Organization extracted via trigger inline")
                                return candidate, "rule_based"
                # Else try next non-blocked line
                j = i + 1
                while j < len(lines) and j in blocked:
                    j += 1
                if j < len(lines):
                    candidate = lines[j].strip()
                    if cls._is_valid_organization(candidate):
                        used_indices.add(j)
                        logger.info("Organization extracted via trigger next line")
                        return candidate, "rule_based"

        return None, "not_found"
    
    @classmethod
    def extract_certificate_title(cls, lines: List[str]) -> Tuple[Optional[str], Optional[int], str]:
        """Extract certificate title with highest priority and return line index"""
        # ALL CAPS with certificate keywords has highest priority
        for idx, line in enumerate(lines):
            if line.isupper() and len(line) > 6 and any(k.upper() in line for k in cls.CERTIFICATE_KEYWORDS):
                logger.info("Certificate title extracted via ALL CAPS detection")
                return line, idx, "rule_based"

        # Mixed case with keywords as fallback
        for idx, line in enumerate(lines):
            if any(k.lower() in line.lower() for k in cls.CERTIFICATE_KEYWORDS) and 6 < len(line) < 200:
                logger.info("Certificate title extracted via keyword matching")
                return line, idx, "rule_based"

        return None, None, "not_found"
    
    @classmethod
    def extract_issue_date(cls, text: str) -> Tuple[Optional[str], str]:
        """
        Extract issue date using rule-based approach
        
        Returns:
            Tuple of (date, extraction_method)
        """
        # Search for date after trigger phrases
        for trigger in cls.DATE_TRIGGERS:
            match = re.search(
                rf'{trigger}\s*[:\-]?\s*(\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{2,4}}|'
                r'\d{{4}}[-/]\d{{1,2}}[-/]\d{{1,2}}|'
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{1,2}},?\s+\d{{4}}|'
                r'\d{{1,2}}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{4}})',
                text, re.IGNORECASE
            )
            if match:
                date_str = match.group(1).strip()
                logger.info(f"Date extracted via rule-based (trigger: {trigger})")
                return date_str, "rule_based"
        
        # Fallback: search for date patterns anywhere
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info("Date extracted via pattern matching")
                return match.group(1).strip(), "rule_based"
        
        return None, "not_found"
    
    @staticmethod
    def _is_valid_name(name: str) -> bool:
        """Validate if string is a reasonable name"""
        if not name:
            return False
        if name.isupper():
            return False
        if any(keyword.lower() in name.lower() for keyword in RuleBasedEntityExtractor.CERTIFICATE_KEYWORDS):
            return False
        if any(char.isdigit() for char in name):
            return False
        # Only alphabetic and spaces
        if not re.fullmatch(r"[A-Za-z\s.'-]+", name):
            return False
        # Reasonable word and length limits
        words = name.split()
        return 1 <= len(words) <= 4 and 3 <= len(name) <= 100
    
    @staticmethod
    def _is_valid_organization(org: str) -> bool:
        """Validate if string is a reasonable organization name"""
        if not org or len(org) < 3 or len(org) > 200:
            return False
        # Should not be mostly numbers
        alpha_chars = sum(1 for c in org if c.isalpha())
        return alpha_chars / len(org) > 0.5
    
    @staticmethod
    def _is_title_case(text: str) -> bool:
        """Check if text is in title case"""
        words = text.split()
        if not words:
            return False
        # At least first word should be capitalized
        return words[0][0].isupper() if words[0] else False


class NERService:
    """
    Hybrid NER Service for certificate entity extraction
    Primary: Rule-based extraction
    Secondary: spaCy NER as fallback
    """
    
    def __init__(self):
        """Initialize NER service with spaCy model"""
        try:
            # Load English language model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("NER service initialized with spaCy model (hybrid approach)")
        except OSError:
            logger.error("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract entities from text using hybrid approach
        Primary: Rule-based, Secondary: spaCy NER fallback
        
        Args:
            text: Input text from certificate
            
        Returns:
            Dictionary with extracted entities and extraction methods
        """
        if not text:
            logger.warning("Empty text provided for entity extraction")
            return self._create_empty_entities()
        
        try:
            # Preprocess text
            text = CertificateTextPreprocessor.preprocess(text)
            lines = CertificateTextPreprocessor.get_lines(text)

            used_indices: set = set()

            # 1) Certificate title FIRST (highest priority)
            certificate_title, cert_idx, cert_method = RuleBasedEntityExtractor.extract_certificate_title(lines)
            if cert_idx is not None:
                used_indices.add(cert_idx)

            # 2) Person name using strict rules, excluding title line
            person_name, person_method = RuleBasedEntityExtractor.extract_person_name(
                lines,
                certificate_title_idx=cert_idx,
                used_indices=used_indices,
            )

            # 3) Organization only after allowed triggers
            organization, org_method = RuleBasedEntityExtractor.extract_organization(
                lines,
                used_indices=used_indices,
                certificate_title_idx=cert_idx,
            )

            # 4) Date using trigger-based patterns
            issue_date, date_method = RuleBasedEntityExtractor.extract_issue_date(text)

            # Validation: avoid person == certificate title
            if person_name and certificate_title and person_name.strip().lower() == certificate_title.strip().lower():
                logger.warning("Discarding person name because it matches certificate title")
                person_name = None
                person_method = "discarded"

            # Fallback to spaCy NER for missing person/organization/date
            if person_name is None or organization is None or issue_date is None:
                spacy_results = self._extract_with_spacy(text)

                if person_name is None and spacy_results.get("person_name"):
                    candidate = spacy_results["person_name"]
                    if RuleBasedEntityExtractor._is_valid_name(candidate) and (
                        not certificate_title or candidate.strip().lower() != certificate_title.strip().lower()
                    ):
                        person_name = candidate
                        person_method = "spacy"
                        logger.info("Person name fallback to spaCy")

                if organization is None and spacy_results.get("organization"):
                    organization = spacy_results["organization"]
                    org_method = "spacy"
                    logger.info("Organization fallback to spaCy")

                if issue_date is None and spacy_results.get("issue_date"):
                    issue_date = spacy_results["issue_date"]
                    date_method = "spacy"
                    logger.info("Date fallback to spaCy")
            
            # Build result with extraction methods logged
            entities = {
                "person_name": person_name,
                "organization": organization,
                "certificate_title": certificate_title,
                "issue_date": issue_date,
                "registration_number": self._extract_registration_number(text),
            }
            
            # Log extraction summary
            self._log_extraction_summary(entities, person_method, org_method, cert_method, date_method)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}", exc_info=True)
            return self._create_empty_entities()
    
    def _extract_with_spacy(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract entities using spaCy NER as fallback
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with spaCy extracted entities
        """
        if not self.nlp:
            return {}
        
        try:
            doc = self.nlp(text)
            
            result = {}
            
            # Extract PERSON entities
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if persons:
                result["person_name"] = persons[0]
            
            # Extract ORG entities
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs:
                result["organization"] = orgs[0]
            
            # Extract DATE entities
            dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
            if dates:
                for date in dates:
                    if any(char.isdigit() for char in date) and len(date) > 4:
                        result["issue_date"] = date
                        break
            
            return result
        
        except Exception as e:
            logger.warning(f"spaCy extraction failed: {str(e)}")
            return {}
    
    def _extract_registration_number(self, text: str) -> Optional[str]:
        """
        Extract registration/certificate number
        
        Args:
            text: Input text
            
        Returns:
            Registration number if found, None otherwise
        """
        # Look for common registration number patterns
        reg_patterns = [
            r"(?:registration|certificate|ref|serial)\s*(?:number|no|#)?:?\s*([A-Z0-9-]+)",
            r"\b([A-Z]{2,}-\d{4}-\d{6})\b",
            r"\b([A-Z]{2}\d{4}\w+)\b",
        ]
        
        for pattern in reg_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.info("Registration number extracted via pattern matching")
                return match.group(1).strip()
        
        return None
    
    def _log_extraction_summary(self, entities: Dict, person_method: str, org_method: str,
                                cert_method: str, date_method: str) -> None:
        """
        Log summary of entity extraction with methods used
        
        Args:
            entities: Extracted entities dictionary
            person_method: Method used for person name extraction
            org_method: Method used for organization extraction
            cert_method: Method used for certificate title extraction
            date_method: Method used for date extraction
        """
        summary = f"Entity extraction summary: "
        summary += f"person_name({person_method}), "
        summary += f"organization({org_method}), "
        summary += f"certificate_title({cert_method}), "
        summary += f"issue_date({date_method})"
        
        # Log missing entities as warnings
        if not entities.get("person_name"):
            logger.warning("Person name not found after extraction attempts")
        if not entities.get("organization"):
            logger.warning("Organization not found after extraction attempts")
        if not entities.get("issue_date"):
            logger.warning("Issue date not found after extraction attempts")
        
        logger.info(summary)
    
    def _create_empty_entities(self) -> Dict[str, Optional[str]]:
        """Create empty entities dictionary"""
        return {
            "person_name": None,
            "organization": None,
            "certificate_title": None,
            "issue_date": None,
            "registration_number": None,
        }


# Global NER service instance
ner_service = NERService()
