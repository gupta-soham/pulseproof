"""
Enhanced Event Processor with Advanced Risk Assessment
Integrates the enhanced risk engine with existing event processing
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import CandidateEvent, ProcessedEvent, EventType, SuspicionLevel
# Import the base EventProcessor functionality directly
# from event_processor import EventProcessor
from enhanced_risk_engine import EnhancedRiskEngine, RiskAssessment, RiskCategory


class EnhancedEventProcessor:
    """
    Enhanced event processor with advanced risk assessment capabilities
    """
    
    def __init__(self, web3_provider_url: Optional[str] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced risk engine
        self.risk_engine = EnhancedRiskEngine(web3_provider_url)
        
        # Enhanced risk factors mapping
        self.ENHANCED_RISK_FACTORS = {
            EventType.TRANSFER: [
                "large_amount_transfer",
                "zero_address_transfer", 
                "contract_to_contract_transfer",
                "unusual_transfer_pattern",
                "high_financial_impact",
                "behavioral_anomaly",
                "reputation_risk"
            ],
            EventType.APPROVAL: [
                "unlimited_approval",
                "large_approval_amount",
                "approval_to_contract",
                "rapid_approval_changes",
                "high_financial_impact",
                "behavioral_anomaly",
                "reputation_risk"
            ]
        }
    
    def preprocess_event(self, candidate_event: CandidateEvent) -> ProcessedEvent:
        """
        Enhanced preprocessing with comprehensive risk assessment
        """
        try:
            # First, do basic preprocessing
            processed_event = super().preprocess_event(candidate_event)
            
            # Then, perform enhanced risk assessment
            risk_assessment = self.risk_engine.assess_comprehensive_risk(processed_event)
            
            # Update suspicion level based on enhanced assessment
            enhanced_suspicion_level = self._map_risk_to_suspicion_level(risk_assessment)
            
            # Merge risk factors
            enhanced_risk_factors = self._merge_risk_factors(
                processed_event.risk_factors,
                risk_assessment.factors
            )
            
            # Create enhanced processed event
            enhanced_event = ProcessedEvent(
                transaction_hash=processed_event.transaction_hash,
                block_number=processed_event.block_number,
                log_index=processed_event.log_index,
                contract_address=processed_event.contract_address,
                event_signature=processed_event.event_signature,
                event_type=processed_event.event_type,
                topics=processed_event.topics,
                data=processed_event.data,
                parsed_data=processed_event.parsed_data,
                suspicion_level=enhanced_suspicion_level,
                risk_factors=enhanced_risk_factors
            )
            
            # Add enhanced assessment data to parsed_data
            enhanced_event.parsed_data.update({
                'enhanced_risk_assessment': {
                    'overall_score': risk_assessment.overall_score,
                    'confidence': risk_assessment.confidence,
                    'risk_category': risk_assessment.risk_category.value,
                    'recommendation': risk_assessment.recommendation,
                    'assessment_timestamp': risk_assessment.details.get('assessment_timestamp')
                }
            })
            
            self.logger.info(f"✅ Enhanced processing completed for {candidate_event.transaction_hash[:10]}...")
            self.logger.info(f"   📊 Risk Score: {risk_assessment.overall_score:.2f}")
            self.logger.info(f"   🎯 Confidence: {risk_assessment.confidence:.2f}")
            self.logger.info(f"   ⚠️  Category: {risk_assessment.risk_category.value}")
            self.logger.info(f"   💡 Recommendation: {risk_assessment.recommendation}")
            
            return enhanced_event
            
        except Exception as e:
            self.logger.error(f"❌ Error in enhanced preprocessing: {e}")
            # Fallback to basic processing
            return super().preprocess_event(candidate_event)
    
    def _map_risk_to_suspicion_level(self, risk_assessment: RiskAssessment) -> SuspicionLevel:
        """
        Map enhanced risk assessment to suspicion level
        """
        score = risk_assessment.overall_score
        confidence = risk_assessment.confidence
        
        # Only upgrade suspicion level if confidence is high enough
        if confidence < 0.6:
            return SuspicionLevel.LOW
        
        if score >= 0.9:
            return SuspicionLevel.CRITICAL
        elif score >= 0.7:
            return SuspicionLevel.HIGH
        elif score >= 0.5:
            return SuspicionLevel.MEDIUM
        else:
            return SuspicionLevel.LOW
    
    def _merge_risk_factors(self, basic_factors: List[str], enhanced_factors: List[str]) -> List[str]:
        """
        Merge basic and enhanced risk factors, removing duplicates
        """
        all_factors = list(set(basic_factors + enhanced_factors))
        
        # Sort factors by priority
        priority_order = [
            "CRITICAL_FINANCIAL_IMPACT",
            "HIGH_FINANCIAL_IMPACT", 
            "UNLIMITED_APPROVAL",
            "BEHAVIORAL_ANOMALY",
            "REPUTATION_RISK",
            "HIGH_ANOMALY_SCORE",
            "MEDIUM_FINANCIAL_IMPACT",
            "LARGE_APPROVAL",
            "MEDIUM_ANOMALY_SCORE",
            "LOW_FINANCIAL_IMPACT",
            "LOW_ANOMALY_SCORE"
        ]
        
        # Sort factors by priority
        sorted_factors = []
        for priority_factor in priority_order:
            if priority_factor in all_factors:
                sorted_factors.append(priority_factor)
                all_factors.remove(priority_factor)
        
        # Add remaining factors
        sorted_factors.extend(sorted(all_factors))
        
        return sorted_factors
    
    def get_risk_summary(self, processed_event: ProcessedEvent) -> Dict[str, Any]:
        """
        Get comprehensive risk summary for an event
        """
        try:
            enhanced_data = processed_event.parsed_data.get('enhanced_risk_assessment', {})
            
            return {
                'transaction_hash': processed_event.transaction_hash,
                'event_type': processed_event.event_type.value,
                'suspicion_level': processed_event.suspicion_level.name,
                'risk_score': enhanced_data.get('overall_score', 0.0),
                'confidence': enhanced_data.get('confidence', 0.0),
                'risk_category': enhanced_data.get('risk_category', 'unknown'),
                'recommendation': enhanced_data.get('recommendation', 'MONITOR'),
                'risk_factors': processed_event.risk_factors,
                'assessment_timestamp': enhanced_data.get('assessment_timestamp')
            }
            
        except Exception as e:
            self.logger.error(f"Error generating risk summary: {e}")
            return {
                'transaction_hash': processed_event.transaction_hash,
                'error': str(e)
            }
    
    def get_financial_impact(self, processed_event: ProcessedEvent) -> Dict[str, Any]:
        """
        Get detailed financial impact analysis
        """
        try:
            enhanced_data = processed_event.parsed_data.get('enhanced_risk_assessment', {})
            risk_components = enhanced_data.get('risk_components', {})
            financial_component = risk_components.get('financial_impact', {})
            
            return {
                'usd_value': financial_component.get('usd_value', 0.0),
                'amount': financial_component.get('amount', 0),
                'token_address': financial_component.get('token_address', ''),
                'impact_level': self._get_impact_level(financial_component.get('usd_value', 0.0)),
                'factors': financial_component.get('factors', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting financial impact: {e}")
            return {'error': str(e)}
    
    def _get_impact_level(self, usd_value: float) -> str:
        """Get human-readable impact level"""
        if usd_value > 1000000:
            return "CRITICAL"
        elif usd_value > 100000:
            return "HIGH"
        elif usd_value > 10000:
            return "MEDIUM"
        elif usd_value > 1000:
            return "LOW"
        else:
            return "MINIMAL"
