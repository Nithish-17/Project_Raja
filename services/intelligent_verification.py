"""
Intelligent Verification Engine with Fuzzy Matching and Confidence Scoring
Implements weighted scoring for comprehensive certificate verification
"""
from typing import Dict, Tuple, List, Any, Optional
from fuzzywuzzy import fuzz
from datetime import datetime
import re

from utils import get_logger

logger = get_logger("verification.intelligent_engine")


class IntelligentVerificationEngine:
    """Advanced verification with fuzzy matching and confidence scoring"""
    
    # Weighted scoring configuration
    WEIGHTS = {
        "person_name": 0.40,
        "organization": 0.30,
        "certificate_title": 0.20,
        "issue_date": 0.10,
    }
    
    # Confidence thresholds
    VERIFIED_THRESHOLD = 85.0
    PARTIALLY_VERIFIED_THRESHOLD = 60.0
    
    def __init__(self):
        """Initialize verification engine"""
        self.valid_certificates = [
            {
                "person_name": "John Smith",
                "organization": "Stanford University",
                "certificate_title": "Machine Learning Specialization",
                "issue_date": "2023-06-15",
                "registration_number": "ML-2023-001234"
            },
            {
                "person_name": "Jane Doe",
                "organization": "MIT",
                "certificate_title": "Data Science Certificate",
                "issue_date": "2023-08-20",
                "registration_number": "DS-2023-005678"
            },
            {
                "person_name": "Alice Johnson",
                "organization": "Harvard University",
                "certificate_title": "Python Programming Certificate",
                "issue_date": "2023-09-10",
                "registration_number": "PY-2023-009012"
            },
            {
                "person_name": "Bob Williams",
                "organization": "Google",
                "certificate_title": "Cloud Architecture Certificate",
                "issue_date": "2023-07-25",
                "registration_number": "GCP-2023-003456"
            },
            {
                "person_name": "Carol Martinez",
                "organization": "IBM",
                "certificate_title": "AI Engineering Certificate",
                "issue_date": "2023-10-05",
                "registration_number": "AI-2023-007890"
            },
        ]
        logger.info("Intelligent Verification Engine initialized")
    
    def verify(
        self,
        extracted_entities: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        """
        Verify certificate with fuzzy matching and confidence scoring
        
        Args:
            extracted_entities: Extracted entities from certificate
            
        Returns:
            Dictionary with verification results including status, score, and details
        """
        try:
            if not extracted_entities or not any(extracted_entities.values()):
                return self._create_result(
                    status="NOT_VERIFIED",
                    confidence_score=0.0,
                    reason="No extractable entities found"
                )
            
            # Find best matching certificate
            best_match = self._find_best_match(extracted_entities)
            
            if best_match["overall_score"] == 0:
                return self._create_result(
                    status="NOT_VERIFIED",
                    confidence_score=0.0,
                    mismatches=best_match["field_scores"],
                    reason="No matching certificate found"
                )
            
            # Determine verification status
            score = best_match["overall_score"]
            if score >= self.VERIFIED_THRESHOLD:
                status = "VERIFIED"
            elif score >= self.PARTIALLY_VERIFIED_THRESHOLD:
                status = "PARTIALLY_VERIFIED"
            else:
                status = "NOT_VERIFIED"
            
            result = self._create_result(
                status=status,
                confidence_score=score,
                field_scores=best_match["field_scores"],
                matched_record=best_match["matched_record"],
                mismatches=best_match["mismatches"]
            )
            
            logger.info(
                f"Verification result: {status} (score: {score:.2f}) "
                f"Name: {extracted_entities.get('person_name', 'N/A')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in verification: {str(e)}")
            return self._create_result(
                status="NOT_VERIFIED",
                confidence_score=0.0,
                reason=f"Verification error: {str(e)}"
            )
    
    def _find_best_match(
        self,
        extracted_entities: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        """Find the best matching certificate from database"""
        best_score = 0.0
        best_match = None
        best_scores = {}
        best_mismatches = {}
        
        for valid_cert in self.valid_certificates:
            # Calculate weighted scores for each field
            field_scores = self._calculate_field_scores(extracted_entities, valid_cert)
            overall_score = self._calculate_overall_score(field_scores)
            
            # Track mismatches
            mismatches = self._identify_mismatches(extracted_entities, valid_cert, field_scores)
            
            if overall_score > best_score:
                best_score = overall_score
                best_match = valid_cert
                best_scores = field_scores
                best_mismatches = mismatches
        
        return {
            "overall_score": best_score,
            "field_scores": best_scores,
            "matched_record": best_match,
            "mismatches": best_mismatches
        }
    
    def _calculate_field_scores(
        self,
        extracted: Dict[str, Optional[str]],
        valid_cert: Dict[str, str]
    ) -> Dict[str, float]:
        """Calculate similarity scores for each field"""
        scores = {}
        
        # Person Name (40%)
        scores["person_name"] = self._fuzzy_match(
            extracted.get("person_name", ""),
            valid_cert.get("person_name", "")
        )
        
        # Organization (30%)
        scores["organization"] = self._fuzzy_match(
            extracted.get("organization", ""),
            valid_cert.get("organization", "")
        )
        
        # Certificate Title (20%)
        scores["certificate_title"] = self._fuzzy_match(
            extracted.get("certificate_title", ""),
            valid_cert.get("certificate_title", "")
        )
        
        # Issue Date (10%)
        scores["issue_date"] = self._date_match_score(
            extracted.get("issue_date", ""),
            valid_cert.get("issue_date", "")
        )
        
        return scores
    
    def _fuzzy_match(self, extracted: str, valid: str) -> float:
        """Calculate fuzzy match score between two strings"""
        if not extracted or not valid:
            return 0.0
        
        # Normalize strings
        extracted_norm = extracted.lower().strip()
        valid_norm = valid.lower().strip()
        
        # Exact match
        if extracted_norm == valid_norm:
            return 100.0
        
        # Use token_set_ratio for partial matches
        score = fuzz.token_set_ratio(extracted_norm, valid_norm)
        
        return float(score)
    
    def _date_match_score(self, extracted_date: str, valid_date: str) -> float:
        """Calculate date match score with fuzzy date parsing"""
        if not extracted_date or not valid_date:
            return 0.0
        
        # Extract year and month if possible
        extracted_date = str(extracted_date).strip()
        valid_date = str(valid_date).strip()
        
        # Exact match
        if extracted_date == valid_date:
            return 100.0
        
        # Try to extract year
        extracted_year = self._extract_year(extracted_date)
        valid_year = self._extract_year(valid_date)
        
        if extracted_year and valid_year and extracted_year == valid_year:
            return 80.0  # Year matches
        
        # Fuzzy match as fallback
        return fuzz.ratio(extracted_date, valid_date)
    
    def _extract_year(self, date_str: str) -> Optional[str]:
        """Extract year from date string"""
        match = re.search(r'(20\d{2})', date_str)
        return match.group(1) if match else None
    
    def _calculate_overall_score(self, field_scores: Dict[str, float]) -> float:
        """Calculate overall confidence score using weighted average"""
        total_score = 0.0
        
        for field, weight in self.WEIGHTS.items():
            score = field_scores.get(field, 0.0)
            total_score += score * weight
        
        return total_score
    
    def _identify_mismatches(
        self,
        extracted: Dict[str, Optional[str]],
        valid_cert: Dict[str, str],
        field_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Identify and document mismatches"""
        mismatches = {}
        
        for field in ["person_name", "organization", "certificate_title", "issue_date"]:
            score = field_scores.get(field, 0.0)
            
            if score < 100.0 and score > 0.0:  # Partial match
                mismatches[field] = {
                    "extracted": extracted.get(field),
                    "expected": valid_cert.get(field),
                    "similarity_score": score
                }
            elif score == 0.0 and extracted.get(field):  # No match
                mismatches[field] = {
                    "extracted": extracted.get(field),
                    "expected": valid_cert.get(field),
                    "similarity_score": 0.0
                }
        
        return mismatches if mismatches else None
    
    def _create_result(
        self,
        status: str,
        confidence_score: float,
        field_scores: Dict[str, float] = None,
        matched_record: Dict[str, str] = None,
        mismatches: Dict[str, Any] = None,
        reason: str = None
    ) -> Dict[str, Any]:
        """Create verification result dictionary"""
        return {
            "verification_status": status,
            "confidence_score": round(confidence_score, 2),
            "field_scores": field_scores or {},
            "matched_record": matched_record,
            "mismatches": mismatches,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        }


# Global verification engine instance
verification_engine = IntelligentVerificationEngine()
