#!/usr/bin/env python3
"""
PulseProof Phase 2 Risk Assessor Agent
Real agent communication using ctx.send and ctx.send_and_receive
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uagents import Agent, Context, Model

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from models import ProcessedEvent, SuspicionLevel
from communication_models import (
    EventAnalysisResult,
    RiskAssessmentRequest,
    RiskAssessmentResult,
    AgentHealthCheck,
    AgentHealthResponse,
    AgentError,
    AgentAcknowledgment
)
from enhanced_risk_engine import EnhancedRiskEngine, RiskAssessment
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "PulseProof-Phase2-RiskAssessor"
AGENT_SEED = "pulseproof_phase2_risk_assessor_seed_phrase_2024"
AGENT_PORT = 8003

# Create the Phase 2 Risk Assessor Agent
risk_assessor = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=False  # Disable mailbox for local testing
)

# Initialize enhanced risk engine
# For now, disable Web3 provider to avoid connection issues
WEB3_PROVIDER_URL = None  # Disabled for now
risk_engine = EnhancedRiskEngine(WEB3_PROVIDER_URL)

# Agent state tracking
agent_state = {
    "assessments_completed": 0,
    "high_risk_assessments": 0,
    "critical_risk_assessments": 0,
    "startup_time": datetime.now(),
    "risk_categories": {
        "financial_impact": 0,
        "behavioral_anomaly": 0,
        "reputation_risk": 0,
        "historical_context": 0,
        "approval_risk": 0
    },
    "api_calls": {
        "etherscan": 0,
        "coingecko": 0,
        "goplus": 0
    },
    "communication_stats": {
        "requests_received": 0,
        "responses_sent": 0,
        "errors_handled": 0
    }
}

@risk_assessor.on_event("startup")
async def startup_handler(ctx: Context):
    """Initialize the Phase 2 risk assessor agent on startup"""
    ctx.logger.info(f"📊 {AGENT_NAME} starting up...")
    ctx.logger.info(f"📍 Agent address: {risk_assessor.address}")
    ctx.logger.info(f"🌐 Agent endpoint: http://localhost:{AGENT_PORT}")
    ctx.logger.info(f"🔍 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={risk_assessor.address}")
    
    ctx.logger.info("ℹ️  Running in Phase 2 mode with real agent communication")
    ctx.logger.info("✅ Phase 2 Risk Assessor Agent initialized successfully")
    ctx.logger.info("📡 Ready to perform risk assessments with real agent communication")

@risk_assessor.on_event("shutdown")
async def shutdown_handler(ctx: Context):
    """Handle agent shutdown gracefully"""
    ctx.logger.info(f"🛑 {AGENT_NAME} shutting down...")
    ctx.logger.info(f"📊 Final stats - Assessments completed: {agent_state['assessments_completed']}")
    ctx.logger.info(f"⚠️  High risk assessments: {agent_state['high_risk_assessments']}")
    ctx.logger.info(f"🚨 Critical risk assessments: {agent_state['critical_risk_assessments']}")
    ctx.logger.info(f"📡 Communication stats: {agent_state['communication_stats']}")

@risk_assessor.on_message(model=EventAnalysisResult)
async def handle_event_analysis_result(ctx: Context, sender: str, msg: EventAnalysisResult):
    """
    Handle event analysis results from Event Analyzer Agent
    Perform comprehensive risk assessment using real agent communication
    """
    ctx.logger.info(f"📊 Received event analysis result {msg.request_id} from {sender}")
    ctx.logger.info(f"   📊 Processed events: {len(msg.processed_events)}")
    ctx.logger.info(f"   🔍 Patterns detected: {len(msg.patterns_detected)}")
    ctx.logger.info(f"   📈 Confidence: {msg.confidence_score:.2f}")
    
    agent_state["communication_stats"]["requests_received"] += 1
    
    start_time = datetime.now()
    risk_assessments = []
    critical_events = []
    recommendations = []
    
    try:
        # Send acknowledgment
        acknowledgment = AgentAcknowledgment(
            request_id=msg.request_id,
            status="processing",
            message=f"Risk Assessor received {len(msg.processed_events)} processed events for risk assessment",
            agent_name=AGENT_NAME,
            timestamp=datetime.now().isoformat()
        )
        await ctx.send(sender, acknowledgment)
        ctx.logger.info(f"📤 Sent acknowledgment for request {msg.request_id}")
        
        # Perform risk assessment on each processed event
        for processed_event in msg.processed_events:
            ctx.logger.info(f"🔍 Assessing risk for event: {processed_event.transaction_hash[:10]}...")
            
            # Perform comprehensive risk assessment
            risk_assessment = risk_engine.assess_comprehensive_risk(processed_event)
            risk_assessments.append({
                "transaction_hash": processed_event.transaction_hash,
                "event_type": processed_event.event_type.value,
                "risk_score": risk_assessment.overall_score,
                "confidence": risk_assessment.confidence,
                "risk_category": risk_assessment.risk_category.value,
                "factors": risk_assessment.factors,
                "recommendation": risk_assessment.recommendation,
                "details": risk_assessment.details
            })
            
            # Track risk categories
            agent_state["risk_categories"][risk_assessment.risk_category.value] += 1
            
            # Identify critical events
            if risk_assessment.overall_score >= Config.CRITICAL_RISK_THRESHOLD:
                critical_events.append({
                    "transaction_hash": processed_event.transaction_hash,
                    "risk_score": risk_assessment.overall_score,
                    "recommendation": risk_assessment.recommendation,
                    "factors": risk_assessment.factors
                })
                agent_state["critical_risk_assessments"] += 1
                recommendations.append(f"CRITICAL: {risk_assessment.recommendation} for {processed_event.transaction_hash[:10]}")
            
            elif risk_assessment.overall_score >= Config.HIGH_RISK_THRESHOLD:
                agent_state["high_risk_assessments"] += 1
                recommendations.append(f"HIGH RISK: {risk_assessment.recommendation} for {processed_event.transaction_hash[:10]}")
            
            # Log assessment details
            ctx.logger.info(f"   📊 Risk score: {risk_assessment.overall_score:.2f}")
            ctx.logger.info(f"   📈 Confidence: {risk_assessment.confidence:.2f}")
            ctx.logger.info(f"   🏷️  Category: {risk_assessment.risk_category.value}")
            ctx.logger.info(f"   💡 Recommendation: {risk_assessment.recommendation}")
            ctx.logger.info(f"   🎯 Factors: {len(risk_assessment.factors)}")
        
        # Calculate overall risk score
        if risk_assessments:
            overall_risk_score = sum(ra["risk_score"] for ra in risk_assessments) / len(risk_assessments)
        else:
            overall_risk_score = 0.0
        
        # Generate additional recommendations based on patterns
        pattern_recommendations = generate_pattern_recommendations(msg.patterns_detected)
        recommendations.extend(pattern_recommendations)
        
        # Calculate assessment time and confidence
        assessment_time = (datetime.now() - start_time).total_seconds()
        confidence_score = calculate_assessment_confidence(risk_assessments, msg.confidence_score)
        
        # Update statistics
        agent_state["assessments_completed"] += 1
        
        # Create result
        result = RiskAssessmentResult(
            risk_assessments=risk_assessments,
            overall_risk_score=overall_risk_score,
            critical_events=critical_events,
            recommendations=recommendations,
            request_id=msg.request_id,
            assessment_time=assessment_time,
            confidence_score=confidence_score
        )
        
        # Send result back to sender (Orchestrator)
        await ctx.send(sender, result)
        agent_state["communication_stats"]["responses_sent"] += 1
        
        ctx.logger.info(f"✅ Risk assessment completed for request {msg.request_id}")
        ctx.logger.info(f"📊 Overall risk score: {overall_risk_score:.2f}")
        ctx.logger.info(f"🚨 Critical events: {len(critical_events)}")
        ctx.logger.info(f"💡 Recommendations: {len(recommendations)}")
        ctx.logger.info(f"⏱️  Assessment time: {assessment_time:.3f}s")
        ctx.logger.info(f"📈 Confidence score: {confidence_score:.2f}")
        ctx.logger.info(f"📤 Sent result to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error assessing risk: {e}")
        agent_state["communication_stats"]["errors_handled"] += 1
        
        # Send error result
        error_result = RiskAssessmentResult(
            risk_assessments=[],
            overall_risk_score=0.0,
            critical_events=[],
            recommendations=[f"Assessment error: {str(e)}"],
            request_id=msg.request_id,
            assessment_time=0.0,
            confidence_score=0.0
        )
        await ctx.send(sender, error_result)
        
        # Send error notification
        error_notification = AgentError(
            error_type="assessment_error",
            error_message=str(e),
            request_id=msg.request_id,
            agent_name=AGENT_NAME,
            timestamp=datetime.now().isoformat()
        )
        await ctx.send(sender, error_notification)

@risk_assessor.on_message(model=AgentHealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: AgentHealthCheck):
    """Handle health check requests from other agents"""
    ctx.logger.info(f"🏥 Received health check from {sender}")
    
    uptime = datetime.now() - agent_state["startup_time"]
    
    health_response = AgentHealthResponse(
        agent_name=AGENT_NAME,
        agent_address=str(risk_assessor.address),
        status="healthy",
        uptime_seconds=uptime.total_seconds(),
        events_processed=agent_state["assessments_completed"],
        timestamp=datetime.now().isoformat()
    )
    
    await ctx.send(sender, health_response)
    ctx.logger.info(f"📤 Sent health response to {sender}")

def generate_pattern_recommendations(patterns_detected: List[Dict[str, Any]]) -> List[str]:
    """
    Generate recommendations based on detected patterns
    Enhanced pattern analysis for Phase 2
    """
    recommendations = []
    
    for pattern in patterns_detected:
        pattern_type = pattern.get("pattern_type", "")
        risk_level = pattern.get("risk_level", "medium")
        
        if pattern_type == "large_transfer":
            recommendations.append(f"Monitor large transfer: {pattern.get('description', '')}")
        elif pattern_type == "unlimited_approval":
            recommendations.append("IMMEDIATE ACTION: Unlimited approval detected - potential exploit risk")
        elif pattern_type == "zero_address_interaction":
            recommendations.append("Investigate zero address interaction - may indicate contract creation or destruction")
        elif pattern_type == "critical_suspicion":
            recommendations.append(f"CRITICAL: {pattern.get('description', '')}")
        elif pattern_type == "multiple_risk_factors":
            recommendations.append(f"High complexity event: {pattern.get('description', '')}")
    
    return recommendations

def calculate_assessment_confidence(risk_assessments: List[Dict[str, Any]], event_confidence: float) -> float:
    """
    Calculate confidence score for the risk assessment
    Enhanced confidence calculation for Phase 2
    """
    if not risk_assessments:
        return 0.0
    
    # Base confidence from event analysis
    base_confidence = event_confidence
    
    # Boost confidence based on assessment quality
    assessment_confidence = sum(ra.get("confidence", 0.0) for ra in risk_assessments) / len(risk_assessments)
    
    # Combine confidences with weights
    final_confidence = (base_confidence * 0.4) + (assessment_confidence * 0.6)
    
    return min(final_confidence, 1.0)

# Response models for REST endpoints
class HealthResponse(Model):
    """Health check response"""
    status: str
    agent_name: str
    agent_address: str
    uptime_seconds: float
    assessments_completed: int
    critical_assessments: int
    timestamp: str

class StatsResponse(Model):
    """Statistics response"""
    agent_info: Dict[str, Any]
    processing_stats: Dict[str, Any]
    communication_stats: Dict[str, Any]
    capabilities: List[str]

@risk_assessor.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Health check endpoint"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return HealthResponse(
        status="healthy",
        agent_name=AGENT_NAME,
        agent_address=str(risk_assessor.address),
        uptime_seconds=uptime.total_seconds(),
        assessments_completed=agent_state["assessments_completed"],
        critical_assessments=agent_state["critical_risk_assessments"],
        timestamp=datetime.now().isoformat()
    )

@risk_assessor.on_rest_get("/stats", StatsResponse)
async def get_stats(ctx: Context) -> StatsResponse:
    """Get detailed agent statistics"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return StatsResponse(
        agent_info={
            "name": AGENT_NAME,
            "address": str(risk_assessor.address),
            "uptime": str(uptime),
            "status": "active"
        },
        processing_stats={
            "total_assessments": agent_state["assessments_completed"],
            "high_risk_assessments": agent_state["high_risk_assessments"],
            "critical_risk_assessments": agent_state["critical_risk_assessments"],
            "risk_categories": agent_state["risk_categories"],
            "api_calls": agent_state["api_calls"]
        },
        communication_stats=agent_state["communication_stats"],
        capabilities=[
            "comprehensive_risk_assessment",
            "multi_factor_analysis",
            "historical_behavior_analysis",
            "reputation_checking",
            "financial_impact_analysis",
            "real_agent_communication"
        ]
    )

if __name__ == "__main__":
    print(f"📊 Starting {AGENT_NAME}...")
    print(f"📍 Agent will be available at: http://localhost:{AGENT_PORT}")
    print(f"🌐 Agent accessible on network at: http://10.200.4.153:{AGENT_PORT}")
    print(f"🔍 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={risk_assessor.address}")
    print("📡 Ready to perform risk assessments with real agent communication")
    print("🏥 Health check available at: GET /health")
    print("📊 Statistics available at: GET /stats")
    print("\n" + "="*60)
    
    risk_assessor.run()
