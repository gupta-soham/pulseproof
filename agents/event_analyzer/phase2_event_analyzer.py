#!/usr/bin/env python3
"""
PulseProof Phase 2 Event Analyzer Agent
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

from models import (
    CandidateEvent, 
    ProcessedEvent, 
    SuspicionLevel,
    EventType
)
from communication_models import (
    EventAnalysisRequest,
    EventAnalysisResult,
    AgentHealthCheck,
    AgentHealthResponse,
    AgentError,
    AgentAcknowledgment
)
from enhanced_event_processor import EnhancedEventProcessor
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "PulseProof-Phase2-EventAnalyzer"
AGENT_SEED = "pulseproof_phase2_event_analyzer_seed_phrase_2024"
AGENT_PORT = 8002

# Create the Phase 2 Event Analyzer Agent
event_analyzer = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=False  # Disable mailbox for local testing
)

# Initialize event processor
event_processor = EnhancedEventProcessor()

# Agent state tracking
agent_state = {
    "events_processed": 0,
    "events_by_type": {},
    "patterns_detected": 0,
    "startup_time": datetime.now(),
    "processing_stats": {
        "transfer_events": 0,
        "approval_events": 0,
        "high_suspicion_events": 0,
        "pattern_matches": 0
    },
    "communication_stats": {
        "requests_received": 0,
        "responses_sent": 0,
        "errors_handled": 0
    }
}

@event_analyzer.on_event("startup")
async def startup_handler(ctx: Context):
    """Initialize the Phase 2 event analyzer agent on startup"""
    ctx.logger.info(f"🔍 {AGENT_NAME} starting up...")
    ctx.logger.info(f"📍 Agent address: {event_analyzer.address}")
    ctx.logger.info(f"🌐 Agent endpoint: http://localhost:{AGENT_PORT}")
    ctx.logger.info(f"🔍 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={event_analyzer.address}")
    
    ctx.logger.info("ℹ️  Running in Phase 2 mode with real agent communication")
    ctx.logger.info("✅ Phase 2 Event Analyzer Agent initialized successfully")
    ctx.logger.info("📡 Ready to analyze blockchain events with real agent communication")

@event_analyzer.on_event("shutdown")
async def shutdown_handler(ctx: Context):
    """Handle agent shutdown gracefully"""
    ctx.logger.info(f"🛑 {AGENT_NAME} shutting down...")
    ctx.logger.info(f"📊 Final stats - Events processed: {agent_state['events_processed']}")
    ctx.logger.info(f"🔍 Patterns detected: {agent_state['patterns_detected']}")
    ctx.logger.info(f"📡 Communication stats: {agent_state['communication_stats']}")

@event_analyzer.on_message(model=EventAnalysisRequest)
async def handle_event_analysis_request(ctx: Context, sender: str, msg: EventAnalysisRequest):
    """
    Handle event analysis requests using real agent communication
    Following Fetch.ai uAgents communication patterns
    """
    ctx.logger.info(f"📥 Received event analysis request {msg.request_id} from {sender}")
    ctx.logger.info(f"   📊 Events to process: {len(msg.candidate_events)}")
    ctx.logger.info(f"   🎯 Priority: {msg.priority}")
    
    agent_state["communication_stats"]["requests_received"] += 1
    
    start_time = datetime.now()
    processed_events = []
    patterns_detected = []
    
    try:
        # Send acknowledgment
        acknowledgment = AgentAcknowledgment(
            request_id=msg.request_id,
            status="processing",
            message=f"Event Analyzer received {len(msg.candidate_events)} events for processing",
            agent_name=AGENT_NAME,
            timestamp=datetime.now().isoformat()
        )
        await ctx.send(sender, acknowledgment)
        ctx.logger.info(f"📤 Sent acknowledgment for request {msg.request_id}")
        
        # Process each candidate event
        for candidate_event in msg.candidate_events:
            ctx.logger.info(f"🔍 Analyzing event: {candidate_event.transaction_hash[:10]}... ({candidate_event.event_type})")
            
            # Preprocess the event
            processed_event = event_processor.preprocess_event(candidate_event)
            processed_events.append(processed_event)
            
            # Update statistics
            agent_state["events_processed"] += 1
            event_type = processed_event.event_type.value
            agent_state["processing_stats"][f"{event_type.lower()}_events"] += 1
            
            if processed_event.suspicion_level.value >= 2:  # HIGH or CRITICAL
                agent_state["processing_stats"]["high_suspicion_events"] += 1
            
            # Detect patterns
            patterns = await detect_patterns(ctx, processed_event)
            patterns_detected.extend(patterns)
            
            # Log analysis results
            ctx.logger.info(f"   📊 Event type: {processed_event.event_type}")
            ctx.logger.info(f"   ⚠️  Suspicion level: {processed_event.suspicion_level.name}")
            ctx.logger.info(f"   🎯 Risk factors: {processed_event.risk_factors}")
            ctx.logger.info(f"   🔍 Patterns detected: {len(patterns)}")
        
        # Calculate processing time and confidence
        processing_time = (datetime.now() - start_time).total_seconds()
        confidence_score = calculate_confidence_score(processed_events, patterns_detected)
        
        # Create analysis summary
        analysis_summary = {
            "total_events": len(processed_events),
            "high_suspicion_events": sum(1 for e in processed_events if e.suspicion_level.value >= 2),
            "patterns_detected": len(patterns_detected),
            "processing_time": processing_time,
            "confidence_score": confidence_score,
            "event_types": {
                event_type: agent_state["processing_stats"][f"{event_type.lower()}_events"]
                for event_type in ["Transfer", "Approval"]
            }
        }
        
        # Create result
        result = EventAnalysisResult(
            processed_events=processed_events,
            patterns_detected=patterns_detected,
            analysis_summary=analysis_summary,
            request_id=msg.request_id,
            processing_time=processing_time,
            confidence_score=confidence_score
        )
        
        # Send result back to sender (Orchestrator)
        await ctx.send(sender, result)
        agent_state["communication_stats"]["responses_sent"] += 1
        
        ctx.logger.info(f"✅ Event analysis completed for request {msg.request_id}")
        ctx.logger.info(f"📈 High suspicion events: {analysis_summary['high_suspicion_events']}")
        ctx.logger.info(f"🔍 Patterns detected: {analysis_summary['patterns_detected']}")
        ctx.logger.info(f"⏱️  Processing time: {processing_time:.3f}s")
        ctx.logger.info(f"📊 Confidence score: {confidence_score:.2f}")
        ctx.logger.info(f"📤 Sent result to {sender}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error analyzing events: {e}")
        agent_state["communication_stats"]["errors_handled"] += 1
        
        # Send error result
        error_result = EventAnalysisResult(
            processed_events=[],
            patterns_detected=[],
            analysis_summary={"error": str(e)},
            request_id=msg.request_id,
            processing_time=0.0,
            confidence_score=0.0
        )
        await ctx.send(sender, error_result)
        
        # Send error notification
        error_notification = AgentError(
            error_type="processing_error",
            error_message=str(e),
            request_id=msg.request_id,
            agent_name=AGENT_NAME,
            timestamp=datetime.now().isoformat()
        )
        await ctx.send(sender, error_notification)

@event_analyzer.on_message(model=AgentHealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: AgentHealthCheck):
    """Handle health check requests from other agents"""
    ctx.logger.info(f"🏥 Received health check from {sender}")
    
    uptime = datetime.now() - agent_state["startup_time"]
    
    health_response = AgentHealthResponse(
        agent_name=AGENT_NAME,
        agent_address=str(event_analyzer.address),
        status="healthy",
        uptime_seconds=uptime.total_seconds(),
        events_processed=agent_state["events_processed"],
        timestamp=datetime.now().isoformat()
    )
    
    await ctx.send(sender, health_response)
    ctx.logger.info(f"📤 Sent health response to {sender}")

async def detect_patterns(ctx: Context, processed_event: ProcessedEvent) -> List[Dict[str, Any]]:
    """
    Detect patterns in the processed event
    Enhanced pattern detection for Phase 2
    """
    patterns = []
    
    try:
        # Pattern 1: Large amount transfers
        if processed_event.event_type == EventType.TRANSFER:
            amount = processed_event.parsed_data.get('amount', 0)
            if amount > 1000000000000000000:  # > 1 ETH in wei
                patterns.append({
                    "pattern_type": "large_transfer",
                    "confidence": 0.8,
                    "description": f"Large transfer detected: {amount} wei",
                    "risk_level": "high",
                    "metadata": {"amount": amount, "threshold": 1000000000000000000}
                })
                agent_state["patterns_detected"] += 1
        
        # Pattern 2: Unlimited approvals
        elif processed_event.event_type == EventType.APPROVAL:
            approval_amount = processed_event.parsed_data.get('approval_amount', 0)
            if approval_amount == 2**256 - 1:  # Max uint256
                patterns.append({
                    "pattern_type": "unlimited_approval",
                    "confidence": 0.9,
                    "description": "Unlimited approval detected",
                    "risk_level": "critical",
                    "metadata": {"approval_amount": approval_amount}
                })
                agent_state["patterns_detected"] += 1
        
        # Pattern 3: Zero address interactions
        from_address = processed_event.parsed_data.get('from_address', '')
        to_address = processed_event.parsed_data.get('to_address', '')
        
        if from_address == '0x0000000000000000000000000000000000000000' or \
           to_address == '0x0000000000000000000000000000000000000000':
            patterns.append({
                "pattern_type": "zero_address_interaction",
                "confidence": 0.7,
                "description": "Zero address interaction detected",
                "risk_level": "medium",
                "metadata": {"from_address": from_address, "to_address": to_address}
            })
            agent_state["patterns_detected"] += 1
        
        # Pattern 4: High suspicion level correlation
        if processed_event.suspicion_level.value >= 3:  # CRITICAL
            patterns.append({
                "pattern_type": "critical_suspicion",
                "confidence": 0.95,
                "description": f"Critical suspicion level: {processed_event.suspicion_level.name}",
                "risk_level": "critical",
                "metadata": {
                    "suspicion_level": processed_event.suspicion_level.name,
                    "risk_factors": processed_event.risk_factors
                }
            })
            agent_state["patterns_detected"] += 1
        
        # Pattern 5: Multiple risk factors
        if len(processed_event.risk_factors) >= 3:
            patterns.append({
                "pattern_type": "multiple_risk_factors",
                "confidence": 0.8,
                "description": f"Multiple risk factors detected: {len(processed_event.risk_factors)}",
                "risk_level": "high",
                "metadata": {
                    "risk_factor_count": len(processed_event.risk_factors),
                    "risk_factors": processed_event.risk_factors
                }
            })
            agent_state["patterns_detected"] += 1
        
        ctx.logger.info(f"🔍 Detected {len(patterns)} patterns for event {processed_event.transaction_hash[:10]}...")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error detecting patterns: {e}")
    
    return patterns

def calculate_confidence_score(processed_events: List[ProcessedEvent], patterns_detected: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence score for the analysis
    Enhanced confidence calculation for Phase 2
    """
    if not processed_events:
        return 0.0
    
    # Base confidence from event processing quality
    base_confidence = 0.7
    
    # Boost confidence based on pattern detection
    pattern_boost = min(len(patterns_detected) * 0.1, 0.3)
    
    # Boost confidence based on data quality
    data_quality_boost = 0.0
    for event in processed_events:
        if event.parsed_data and len(event.parsed_data) > 0:
            data_quality_boost += 0.05
    
    # Cap at 1.0
    confidence = min(base_confidence + pattern_boost + data_quality_boost, 1.0)
    
    return confidence

# Response models for REST endpoints
class HealthResponse(Model):
    """Health check response"""
    status: str
    agent_name: str
    agent_address: str
    uptime_seconds: float
    events_processed: int
    patterns_detected: int
    timestamp: str

class StatsResponse(Model):
    """Statistics response"""
    agent_info: Dict[str, Any]
    processing_stats: Dict[str, Any]
    communication_stats: Dict[str, Any]
    capabilities: List[str]

@event_analyzer.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Health check endpoint"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return HealthResponse(
        status="healthy",
        agent_name=AGENT_NAME,
        agent_address=str(event_analyzer.address),
        uptime_seconds=uptime.total_seconds(),
        events_processed=agent_state["events_processed"],
        patterns_detected=agent_state["patterns_detected"],
        timestamp=datetime.now().isoformat()
    )

@event_analyzer.on_rest_get("/stats", StatsResponse)
async def get_stats(ctx: Context) -> StatsResponse:
    """Get detailed agent statistics"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return StatsResponse(
        agent_info={
            "name": AGENT_NAME,
            "address": str(event_analyzer.address),
            "uptime": str(uptime),
            "status": "active"
        },
        processing_stats=agent_state["processing_stats"],
        communication_stats=agent_state["communication_stats"],
        capabilities=[
            "event_preprocessing",
            "pattern_detection",
            "event_classification",
            "metadata_extraction",
            "real_agent_communication"
        ]
    )

if __name__ == "__main__":
    print(f"🔍 Starting {AGENT_NAME}...")
    print(f"📍 Agent will be available at: http://localhost:{AGENT_PORT}")
    print(f"🌐 Agent accessible on network at: http://10.200.4.153:{AGENT_PORT}")
    print(f"🔍 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={event_analyzer.address}")
    print("📡 Ready to analyze blockchain events with real agent communication")
    print("🏥 Health check available at: GET /health")
    print("📊 Statistics available at: GET /stats")
    print("\n" + "="*60)
    
    event_analyzer.run()
