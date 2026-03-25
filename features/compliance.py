"""
SEBI Compliance and Regulatory Module for ET AI Concierge
Ensures all recommendations comply with Indian financial regulations
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ComplianceLevel(Enum):
    """Compliance levels for different types of advice"""
    EDUCATIONAL = "educational"  # General financial education
    INFORMATIONAL = "informational"  # Market information
    ADVISORY = "advisory"  # Investment advice (requires SEBI registration)
    EXECUTION = "execution"  # Trade execution (requires broker license)

class RiskCategory(Enum):
    """SEBI risk categories"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ComplianceCheck:
    """Result of a compliance check"""
    passed: bool
    level: ComplianceLevel
    warnings: List[str]
    required_disclaimers: List[str]
    risk_category: RiskCategory
    sebi_compliant: bool

class SEBIComplianceEngine:
    """SEBI compliance engine for financial recommendations"""
    
    def __init__(self):
        self.sebi_guidelines = self._load_sebi_guidelines()
        self.risk_matrices = self._load_risk_matrices()
        self.prohibited_terms = self._load_prohibited_terms()
        
    def _load_sebi_guidelines(self) -> Dict[str, Any]:
        """Load SEBI guidelines and regulations"""
        return {
            "investment_advisor_regulations": {
                "registration_required_for": [
                    "specific stock recommendations",
                    "portfolio allocation advice",
                    "timing recommendations",
                    "buy/sell decisions"
                ],
                "educational_content_allowed": [
                    "general market information",
                    "investment concepts",
                    "product features",
                    "risk explanations"
                ]
            },
            "disclosure_requirements": {
                "risk_warnings": [
                    "Mutual fund investments are subject to market risks",
                    "Past performance is not indicative of future results",
                    "Please read all scheme related documents carefully"
                ],
                "general_disclaimers": [
                    "This is for educational purposes only",
                    "Consult a qualified financial advisor before investing",
                    "ET does not guarantee returns or provide investment advice"
                ]
            },
            "prohibited_activities": [
                "Guaranteed returns promises",
                "Specific timing recommendations",
                "Individual stock tips",
                "Portfolio management without license"
            ]
        }
    
    def _load_risk_matrices(self) -> Dict[str, Any]:
        """Load risk assessment matrices"""
        return {
            "product_risk_levels": {
                "savings_account": RiskCategory.LOW,
                "fixed_deposit": RiskCategory.LOW,
                "liquid_funds": RiskCategory.LOW,
                "debt_funds": RiskCategory.MODERATE,
                "hybrid_funds": RiskCategory.MODERATE,
                "equity_funds": RiskCategory.HIGH,
                "small_cap_funds": RiskCategory.VERY_HIGH,
                "derivatives": RiskCategory.VERY_HIGH,
                "crypto": RiskCategory.VERY_HIGH
            },
            "user_risk_tolerance": {
                "conservative": [RiskCategory.LOW],
                "moderate": [RiskCategory.LOW, RiskCategory.MODERATE],
                "aggressive": [RiskCategory.LOW, RiskCategory.MODERATE, RiskCategory.HIGH],
                "very_aggressive": [RiskCategory.LOW, RiskCategory.MODERATE, RiskCategory.HIGH, RiskCategory.VERY_HIGH]
            }
        }
    
    def _load_prohibited_terms(self) -> List[str]:
        """Load terms that cannot be used in recommendations"""
        return [
            "guaranteed returns",
            "risk-free investment",
            "sure shot winner",
            "100% safe",
            "no risk",
            "guaranteed profit",
            "insider tip",
            "hot stock",
            "buy now",
            "sell immediately"
        ]
    
    def check_recommendation_compliance(self, recommendation: Dict[str, Any], 
                                      user_profile: Dict[str, Any]) -> ComplianceCheck:
        """Check if a recommendation is SEBI compliant"""
        
        warnings = []
        disclaimers = []
        compliance_level = ComplianceLevel.EDUCATIONAL
        
        # Check content for prohibited terms
        content_text = (recommendation.get('title', '') + ' ' + 
                       recommendation.get('description', '')).lower()
        
        for term in self.prohibited_terms:
            if term in content_text:
                warnings.append(f"Contains prohibited term: '{term}'")
        
        # Determine compliance level based on content
        if any(phrase in content_text for phrase in ["buy", "sell", "invest in", "allocate"]):
            compliance_level = ComplianceLevel.ADVISORY
            disclaimers.extend(self.sebi_guidelines["disclosure_requirements"]["risk_warnings"])
        
        # Check risk alignment
        product_type = recommendation.get('productType', '').lower()
        product_risk = self.risk_matrices["product_risk_levels"].get(product_type, RiskCategory.HIGH)
        
        user_risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        allowed_risks = self.risk_matrices["user_risk_tolerance"].get(user_risk_tolerance, [RiskCategory.LOW])
        
        if product_risk not in allowed_risks:
            warnings.append(f"Product risk ({product_risk.value}) exceeds user tolerance ({user_risk_tolerance})")
        
        # Add mandatory disclaimers
        disclaimers.extend(self.sebi_guidelines["disclosure_requirements"]["general_disclaimers"])
        
        # Determine SEBI compliance
        sebi_compliant = len(warnings) == 0 and compliance_level in [ComplianceLevel.EDUCATIONAL, ComplianceLevel.INFORMATIONAL]
        
        return ComplianceCheck(
            passed=sebi_compliant,
            level=compliance_level,
            warnings=warnings,
            required_disclaimers=disclaimers,
            risk_category=product_risk,
            sebi_compliant=sebi_compliant
        )
    
    def sanitize_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize recommendation to ensure compliance"""
        sanitized = recommendation.copy()
        
        # Replace prohibited terms
        for field in ['title', 'description']:
            if field in sanitized:
                content = sanitized[field]
                for term in self.prohibited_terms:
                    if term in content.lower():
                        # Replace with compliant alternatives
                        content = content.replace(term, self._get_compliant_alternative(term))
                sanitized[field] = content
        
        # Add compliance tags
        sanitized['compliance_level'] = ComplianceLevel.EDUCATIONAL.value
        sanitized['sebi_compliant'] = True
        
        return sanitized
    
    def _get_compliant_alternative(self, prohibited_term: str) -> str:
        """Get compliant alternative for prohibited terms"""
        alternatives = {
            "guaranteed returns": "potential returns",
            "risk-free investment": "lower-risk investment",
            "sure shot winner": "historically performing",
            "100% safe": "relatively safer",
            "no risk": "lower risk",
            "guaranteed profit": "potential gains",
            "buy now": "consider exploring",
            "sell immediately": "review your holdings"
        }
        return alternatives.get(prohibited_term, "investment option")
    
    def generate_compliance_report(self, recommendations: List[Dict[str, Any]], 
                                 user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        total_recommendations = len(recommendations)
        compliant_count = 0
        warnings_summary = []
        risk_distribution = {risk.value: 0 for risk in RiskCategory}
        
        detailed_checks = []
        
        for rec in recommendations:
            check = self.check_recommendation_compliance(rec, user_profile)
            detailed_checks.append({
                'recommendation_id': rec.get('id', 'unknown'),
                'title': rec.get('title', 'Unknown'),
                'compliance_check': check
            })
            
            if check.sebi_compliant:
                compliant_count += 1
            
            warnings_summary.extend(check.warnings)
            risk_distribution[check.risk_category.value] += 1
        
        compliance_score = (compliant_count / total_recommendations * 100) if total_recommendations > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_recommendations': total_recommendations,
            'compliant_recommendations': compliant_count,
            'compliance_score': compliance_score,
            'risk_distribution': risk_distribution,
            'warnings_summary': list(set(warnings_summary)),  # Remove duplicates
            'detailed_checks': detailed_checks,
            'overall_status': 'COMPLIANT' if compliance_score >= 95 else 'NEEDS_REVIEW',
            'sebi_registration_required': any(
                check.compliance_check.level == ComplianceLevel.ADVISORY 
                for check in detailed_checks
            )
        }

class DataPrivacyCompliance:
    """Data privacy and GDPR/DPDP compliance"""
    
    def __init__(self):
        self.data_categories = self._define_data_categories()
        self.retention_policies = self._define_retention_policies()
    
    def _define_data_categories(self) -> Dict[str, Dict[str, Any]]:
        """Define data categories and their sensitivity levels"""
        return {
            'personal_identifiable': {
                'fields': ['name', 'email', 'phone', 'address', 'pan', 'aadhaar'],
                'sensitivity': 'high',
                'encryption_required': True,
                'retention_days': 2555  # 7 years as per Indian regulations
            },
            'financial_data': {
                'fields': ['income', 'investments', 'bank_details', 'portfolio'],
                'sensitivity': 'very_high',
                'encryption_required': True,
                'retention_days': 2555
            },
            'behavioral_data': {
                'fields': ['click_patterns', 'reading_history', 'preferences'],
                'sensitivity': 'medium',
                'encryption_required': False,
                'retention_days': 365
            },
            'technical_data': {
                'fields': ['ip_address', 'device_info', 'session_data'],
                'sensitivity': 'low',
                'encryption_required': False,
                'retention_days': 90
            }
        }
    
    def _define_retention_policies(self) -> Dict[str, int]:
        """Define data retention policies in days"""
        return {
            'user_sessions': 30,
            'chat_transcripts': 365,
            'recommendation_history': 1095,  # 3 years
            'compliance_logs': 2555,  # 7 years
            'analytics_data': 730,  # 2 years
            'error_logs': 90
        }
    
    def check_data_handling_compliance(self, data_type: str, 
                                     storage_duration: int) -> Dict[str, Any]:
        """Check if data handling is compliant"""
        
        if data_type not in self.data_categories:
            return {
                'compliant': False,
                'reason': f'Unknown data type: {data_type}'
            }
        
        category = self.data_categories[data_type]
        max_retention = category['retention_days']
        
        compliant = storage_duration <= max_retention
        
        return {
            'compliant': compliant,
            'data_type': data_type,
            'sensitivity': category['sensitivity'],
            'max_retention_days': max_retention,
            'current_retention_days': storage_duration,
            'encryption_required': category['encryption_required'],
            'recommendation': 'Compliant' if compliant else f'Reduce retention to {max_retention} days'
        }

# Usage example and testing
if __name__ == "__main__":
    # Test compliance engine
    compliance_engine = SEBIComplianceEngine()
    
    # Sample recommendation
    sample_recommendation = {
        'id': 'rec_001',
        'title': 'Consider SIP in Equity Mutual Funds',
        'description': 'Systematic Investment Plans can help build wealth over time',
        'productType': 'equity_funds'
    }
    
    # Sample user profile
    sample_user = {
        'risk_tolerance': 'moderate',
        'investment_experience': 'beginner',
        'age': 30
    }
    
    # Check compliance
    compliance_check = compliance_engine.check_recommendation_compliance(
        sample_recommendation, sample_user
    )
    
    print("Compliance Check Result:")
    print(f"SEBI Compliant: {compliance_check.sebi_compliant}")
    print(f"Compliance Level: {compliance_check.level.value}")
    print(f"Risk Category: {compliance_check.risk_category.value}")
    print(f"Warnings: {compliance_check.warnings}")
    print(f"Required Disclaimers: {len(compliance_check.required_disclaimers)}")