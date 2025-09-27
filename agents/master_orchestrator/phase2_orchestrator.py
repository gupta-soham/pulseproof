#!/usr/bin/env python3
"""
PulseProof Phase 2 Master Orchestrator Agent
Real agent communication using ctx.send and ctx.send_and_receive
Following Fetch.ai uAgents communication patterns
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
    EventAnalysisRequest, 
    EventAnalysisResponse,
    EventAcknowledgment,
    HealthResponse,
    StatsResponse
)
from communication_models import (
    EventAnalysisRequest as AgentEventAnalysisRequest,
    EventAnalysisResult,
    RiskAssessmentResult,
    OrchestratorRequest,
    OrchestratorResponse,
    AgentHealthCheck,
    AgentHealthResponse,
    AgentError,
    AgentAcknowledgment
)
from local_agent_discovery import discovery_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "PulseProof-Phase2-Orchestrator"
AGENT_SEED = "pulseproof_phase2_orchestrator_seed_phrase_2024"
AGENT_PORT = 8001

# Create the Phase 2 Master Orchestrator Agent
orchestrator = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    mailbox=False  # Disable mailbox for local testing
)

# Agent state tracking
agent_state = {
    "events_processed": 0,
    "high_risk_events": 0,
    "critical_events": 0,
    "startup_time": datetime.now(),
    "sub_agents": {
        "event_analyzer": None,
        "risk_assessor": None
    },
    "delegation_stats": {
        "event_analyzer_calls": 0,
        "risk_assessor_calls": 0,
        "successful_delegations": 0,
        "failed_delegations": 0
    },
    "agent_health": {
        "event_analyzer": "unknown",
        "risk_assessor": "unknown"
    },
    "communication_stats": {
        "requests_received": 0,
        "responses_sent": 0,
        "errors_handled": 0,
        "timeouts": 0
    }
}

@orchestrator.on_event("startup")
async def startup_handler(ctx: Context):
    """Initialize the Phase 2 orchestrator agent on startup"""
    ctx.logger.info(f"🧠 {AGENT_NAME} starting up...")
    ctx.logger.info(f"📍 Agent address: {orchestrator.address}")
    ctx.logger.info(f"🌐 Agent endpoint: http://localhost:{AGENT_PORT}")
    ctx.logger.info(f"🔍 Agent inspector: https://Agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A{AGENT_PORT}&address={orchestrator.address}")
    
    # Discover and register sub-agents
    await discover_sub_agents(ctx)
    
    ctx.logger.info("ℹ️  Running in Phase 2 mode with real agent communication")
    ctx.logger.info("✅ Phase 2 Master Orchestrator Agent initialized successfully")
    ctx.logger.info("📡 Ready to coordinate multi-agent blockchain security analysis with real communication")

async def discover_sub_agents(ctx: Context):
    """Discover and register sub-agents using local discovery service"""
    ctx.logger.info("🔍 Discovering sub-agents using local discovery service...")
    
    # Discover Event Analyzer Agent
    event_analyzer_info = discovery_service.discover_agent("event_analyzer")
    if event_analyzer_info:
        agent_state["sub_agents"]["event_analyzer"] = event_analyzer_info["address"]
        ctx.logger.info(f"✅ Event Analyzer Agent discovered: {event_analyzer_info['name']}")
        ctx.logger.info(f"   📍 Address: {event_analyzer_info['address']}")
        ctx.logger.info(f"   🌐 Port: {event_analyzer_info['port']}")
        ctx.logger.info(f"   🔧 Capabilities: {', '.join(event_analyzer_info['capabilities'])}")
    else:
        ctx.logger.error("❌ Event Analyzer Agent not found")
    
    # Discover Risk Assessor Agent
    risk_assessor_info = discovery_service.discover_agent("risk_assessor")
    if risk_assessor_info:
        agent_state["sub_agents"]["risk_assessor"] = risk_assessor_info["address"]
        ctx.logger.info(f"✅ Risk Assessor Agent discovered: {risk_assessor_info['name']}")
        ctx.logger.info(f"   📍 Address: {risk_assessor_info['address']}")
        ctx.logger.info(f"   🌐 Port: {risk_assessor_info['port']}")
        ctx.logger.info(f"   🔧 Capabilities: {', '.join(risk_assessor_info['capabilities'])}")
    else:
        ctx.logger.error("❌ Risk Assessor Agent not found")
    
    # Check agent health using real agent communication
    await check_agent_health(ctx)

async def check_agent_health(ctx: Context):
    """Check health of all sub-agents using real agent communication"""
    ctx.logger.info("🏥 Checking sub-agent health using real agent communication...")
    
    for agent_type, agent_address in agent_state["sub_agents"].items():
        if agent_address:
            try:
                # Send health check request to agent
                health_check = AgentHealthCheck(
                    requester=str(orchestrator.address),
                    timestamp=datetime.now().isoformat()
                )
                
                # Use ctx.send_and_receive for synchronous communication
                response, status = await ctx.send_and_receive(
                    agent_address,
                    health_check,
                    response_type=AgentHealthResponse,
                    timeout=5.0  # 5 second timeout
                )
                
                if status == "success" and isinstance(response, AgentHealthResponse):
                    agent_state["agent_health"][agent_type] = "healthy"
                    ctx.logger.info(f"✅ {agent_type} agent is healthy")
                    ctx.logger.info(f"   📊 Events processed: {response.events_processed}")
                    ctx.logger.info(f"   ⏱️  Uptime: {response.uptime_seconds:.2f}s")
                else:
                    agent_state["agent_health"][agent_type] = "unhealthy"
                    ctx.logger.warning(f"⚠️ {agent_type} agent health check failed: {status}")
                    
            except Exception as e:
                agent_state["agent_health"][agent_type] = "unreachable"
                ctx.logger.error(f"❌ {agent_type} agent health check error: {e}")
        else:
            agent_state["agent_health"][agent_type] = "not_found"
            ctx.logger.error(f"❌ {agent_type} agent not found")

@orchestrator.on_event("shutdown")
async def shutdown_handler(ctx: Context):
    """Handle agent shutdown gracefully"""
    ctx.logger.info(f"🛑 {AGENT_NAME} shutting down...")
    ctx.logger.info(f"📊 Final stats - Events processed: {agent_state['events_processed']}")
    ctx.logger.info(f"⚠️  High risk events: {agent_state['high_risk_events']}")
    ctx.logger.info(f"🚨 Critical events: {agent_state['critical_events']}")
    ctx.logger.info(f"📡 Communication stats: {agent_state['communication_stats']}")

@orchestrator.on_rest_post("/analyze-events", EventAnalysisRequest, EventAnalysisResponse)
async def analyze_events_endpoint(ctx: Context, request: EventAnalysisRequest) -> EventAnalysisResponse:
    """
    Enhanced REST endpoint with real agent communication
    Using ctx.send_and_receive for synchronous communication
    """
    ctx.logger.info(f"📥 Received event analysis request with {len(request.events)} events")
    agent_state["communication_stats"]["requests_received"] += 1
    
    try:
        # Generate request ID for tracking
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(request.events)}"
        
        # Step 1: Delegate to Event Analyzer Agent using real communication
        ctx.logger.info("🔍 Delegating to Event Analyzer Agent using real communication...")
        event_analysis_result = await delegate_to_event_analyzer(ctx, request, request_id)
        
        if not event_analysis_result:
            return create_error_response(request_id, "Event analysis failed")
        
        # Step 2: Delegate to Risk Assessor Agent using real communication
        ctx.logger.info("📊 Delegating to Risk Assessor Agent using real communication...")
        risk_assessment_result = await delegate_to_risk_assessor(ctx, event_analysis_result, request_id)
        
        if not risk_assessment_result:
            return create_error_response(request_id, "Risk assessment failed")
        
        # Step 3: Synthesize results
        ctx.logger.info("🧠 Synthesizing results...")
        synthesis_result = synthesize_results(event_analysis_result, risk_assessment_result)
        
        # Update statistics
        agent_state["events_processed"] += len(request.events)
        agent_state["high_risk_events"] += synthesis_result["high_risk_count"]
        agent_state["critical_events"] += synthesis_result["critical_count"]
        agent_state["communication_stats"]["successful_delegations"] += 1
        
        # Create acknowledgment response
        acknowledgment = EventAcknowledgment(
            request_id=request_id,
            events_received=len(request.events),
            status="processed",
            message=f"Successfully processed {len(request.events)} events with real multi-agent analysis",
            processing_started=True
        )
        
        ctx.logger.info(f"✅ Real multi-agent analysis completed for request {request_id}")
        ctx.logger.info(f"📈 High risk events: {synthesis_result['high_risk_count']}")
        ctx.logger.info(f"🚨 Critical events: {synthesis_result['critical_count']}")
        ctx.logger.info(f"💡 Recommendations: {len(synthesis_result['recommendations'])}")
        ctx.logger.info(f"📊 Overall risk score: {risk_assessment_result.overall_risk_score:.2f}")
        
        # Return enhanced response
        return EventAnalysisResponse(
            status="success",
            acknowledgment=acknowledgment,
            summary={
                "total_events": len(request.events),
                "processed_events": len(event_analysis_result.processed_events),
                "high_risk_events": synthesis_result["high_risk_count"],
                "critical_events": synthesis_result["critical_count"],
                "patterns_detected": len(event_analysis_result.patterns_detected),
                "recommendations": synthesis_result["recommendations"],
                "overall_risk_score": risk_assessment_result.overall_risk_score,
                "processing_time": event_analysis_result.processing_time + risk_assessment_result.assessment_time,
                "confidence_score": (event_analysis_result.confidence_score + risk_assessment_result.confidence_score) / 2,
                "request_id": request_id,
                "communication_method": "real_agent_communication"
            }
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in real multi-agent processing: {e}")
        agent_state["communication_stats"]["failed_delegations"] += 1
        agent_state["communication_stats"]["errors_handled"] += 1
        return create_error_response(request_id, f"Real multi-agent processing failed: {str(e)}")

async def delegate_to_event_analyzer(ctx: Context, request: EventAnalysisRequest, request_id: str) -> Optional[EventAnalysisResult]:
    """Delegate event analysis to Event Analyzer Agent using real communication"""
    try:
        # Check if Event Analyzer is available
        if agent_state["agent_health"]["event_analyzer"] != "healthy":
            ctx.logger.error("❌ Event Analyzer Agent is not healthy")
            return None
        
        # Create analysis request for Event Analyzer
        analysis_request = AgentEventAnalysisRequest(
            candidate_events=request.events,
            request_id=request_id,
            priority="normal"
        )
        
        # Get Event Analyzer address
        event_analyzer_address = agent_state["sub_agents"]["event_analyzer"]
        if not event_analyzer_address:
            ctx.logger.error("❌ Event Analyzer Agent address not found")
            return None
        
        ctx.logger.info(f"📤 Sending request to Event Analyzer Agent at {event_analyzer_address}")
        
        # Use ctx.send_and_receive for real agent communication
        response, status = await ctx.send_and_receive(
            event_analyzer_address,
            analysis_request,
            response_type=EventAnalysisResult,
            timeout=30.0  # 30 second timeout for event analysis
        )
        
        if status == "success" and isinstance(response, EventAnalysisResult):
            agent_state["delegation_stats"]["event_analyzer_calls"] += 1
            ctx.logger.info("✅ Event Analyzer Agent processing completed")
            ctx.logger.info(f"   📊 Processed events: {len(response.processed_events)}")
            ctx.logger.info(f"   🔍 Patterns detected: {len(response.patterns_detected)}")
            ctx.logger.info(f"   📈 Confidence: {response.confidence_score:.2f}")
            return response
        else:
            ctx.logger.error(f"❌ Event Analyzer Agent communication failed: {status}")
            agent_state["communication_stats"]["timeouts"] += 1
            return None
        
    except Exception as e:
        ctx.logger.error(f"❌ Error delegating to Event Analyzer: {e}")
        agent_state["communication_stats"]["errors_handled"] += 1
        return None

async def delegate_to_risk_assessor(ctx: Context, event_analysis_result: EventAnalysisResult, request_id: str) -> Optional[RiskAssessmentResult]:
    """Delegate risk assessment to Risk Assessor Agent using real communication"""
    try:
        # Check if Risk Assessor is available
        if agent_state["agent_health"]["risk_assessor"] != "healthy":
            ctx.logger.error("❌ Risk Assessor Agent is not healthy")
            return None
        
        # Create risk assessment request for Risk Assessor
        risk_request = RiskAssessmentRequest(
            processed_events=event_analysis_result.processed_events,
            patterns_detected=event_analysis_result.patterns_detected,
            request_id=request_id,
            priority="normal"
        )
        
        # Get Risk Assessor address
        risk_assessor_address = agent_state["sub_agents"]["risk_assessor"]
        if not risk_assessor_address:
            ctx.logger.error("❌ Risk Assessor Agent address not found")
            return None
        
        ctx.logger.info(f"📤 Sending request to Risk Assessor Agent at {risk_assessor_address}")
        
        # Use ctx.send_and_receive for real agent communication
        response, status = await ctx.send_and_receive(
            risk_assessor_address,
            risk_request,
            response_type=RiskAssessmentResult,
            timeout=30.0  # 30 second timeout for risk assessment
        )
        
        if status == "success" and isinstance(response, RiskAssessmentResult):
            agent_state["delegation_stats"]["risk_assessor_calls"] += 1
            ctx.logger.info("✅ Risk Assessor Agent processing completed")
            ctx.logger.info(f"   📊 Risk assessments: {len(response.risk_assessments)}")
            ctx.logger.info(f"   🚨 Critical events: {len(response.critical_events)}")
            ctx.logger.info(f"   💡 Recommendations: {len(response.recommendations)}")
            ctx.logger.info(f"   📈 Overall risk score: {response.overall_risk_score:.2f}")
            return response
        else:
            ctx.logger.error(f"❌ Risk Assessor Agent communication failed: {status}")
            agent_state["communication_stats"]["timeouts"] += 1
            return None
        
    except Exception as e:
        ctx.logger.error(f"❌ Error delegating to Risk Assessor: {e}")
        agent_state["communication_stats"]["errors_handled"] += 1
        return None

def synthesize_results(event_analysis_result: EventAnalysisResult, risk_assessment_result: RiskAssessmentResult) -> Dict[str, Any]:
    """Synthesize results from all agents"""
    high_risk_count = sum(1 for ra in risk_assessment_result.risk_assessments if ra["risk_score"] >= 0.7)
    critical_count = len(risk_assessment_result.critical_events)
    
    return {
        "high_risk_count": high_risk_count,
        "critical_count": critical_count,
        "recommendations": risk_assessment_result.recommendations,
        "patterns_detected": len(event_analysis_result.patterns_detected),
        "overall_confidence": (event_analysis_result.confidence_score + risk_assessment_result.confidence_score) / 2
    }

def create_error_response(request_id: str, error_message: str) -> EventAnalysisResponse:
    """Create error response"""
    return EventAnalysisResponse(
        status="error",
        acknowledgment=EventAcknowledgment(
            request_id=request_id,
            events_received=0,
            status="error",
            message=error_message,
            processing_started=False
        ),
        summary={"error": error_message}
    )

@orchestrator.on_message(model=EventAnalysisResult)
async def handle_event_analysis_result(ctx: Context, sender: str, msg: EventAnalysisResult):
    """Handle results from Event Analyzer Agent"""
    ctx.logger.info(f"📥 Received event analysis result from {sender}")
    ctx.logger.info(f"   📊 Processed events: {len(msg.processed_events)}")
    ctx.logger.info(f"   🔍 Patterns detected: {len(msg.patterns_detected)}")
    ctx.logger.info(f"   📈 Confidence: {msg.confidence_score:.2f}")

@orchestrator.on_message(model=RiskAssessmentResult)
async def handle_risk_assessment_result(ctx: Context, sender: str, msg: RiskAssessmentResult):
    """Handle results from Risk Assessor Agent"""
    ctx.logger.info(f"📥 Received risk assessment result from {sender}")
    ctx.logger.info(f"   📊 Risk assessments: {len(msg.risk_assessments)}")
    ctx.logger.info(f"   🚨 Critical events: {len(msg.critical_events)}")
    ctx.logger.info(f"   💡 Recommendations: {len(msg.recommendations)}")
    ctx.logger.info(f"   📈 Overall risk score: {msg.overall_risk_score:.2f}")

@orchestrator.on_message(model=AgentError)
async def handle_agent_error(ctx: Context, sender: str, msg: AgentError):
    """Handle error messages from sub-agents"""
    ctx.logger.error(f"❌ Received error from {sender}: {msg.error_message}")
    agent_state["communication_stats"]["errors_handled"] += 1

@orchestrator.on_message(model=AgentAcknowledgment)
async def handle_agent_acknowledgment(ctx: Context, sender: str, msg: AgentAcknowledgment):
    """Handle acknowledgment messages from sub-agents"""
    ctx.logger.info(f"📥 Received acknowledgment from {sender}: {msg.message}")

@orchestrator.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Enhanced health check endpoint"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return HealthResponse(
        status="healthy",
        agent_name=AGENT_NAME,
        agent_address=str(orchestrator.address),
        uptime_seconds=uptime.total_seconds(),
        events_processed=agent_state["events_processed"],
        high_risk_events=agent_state["high_risk_events"],
        timestamp=datetime.now().isoformat()
    )

@orchestrator.on_rest_get("/stats", StatsResponse)
async def get_stats(ctx: Context) -> StatsResponse:
    """Enhanced statistics endpoint"""
    uptime = datetime.now() - agent_state["startup_time"]
    
    return StatsResponse(
        agent_info={
            "name": AGENT_NAME,
            "address": str(orchestrator.address),
            "uptime": str(uptime),
            "status": "active"
        },
        processing_stats={
            "total_events_processed": agent_state["events_processed"],
            "high_risk_events": agent_state["high_risk_events"],
            "critical_events": agent_state["critical_events"],
            "low_risk_events": agent_state["events_processed"] - agent_state["high_risk_events"] - agent_state["critical_events"],
            "processing_rate": agent_state["events_processed"] / max(uptime.total_seconds(), 1)
        },
        capabilities=[
            "real_agent_communication",
            "event_analysis_delegation",
            "risk_assessment_delegation",
            "result_synthesis",
            "agent_discovery",
            "synchronous_communication",
            "asynchronous_communication"
        ],
        sub_agents=agent_state["sub_agents"],
        delegation_stats=agent_state["delegation_stats"],
        agent_health=agent_state["agent_health"],
        communication_stats=agent_state["communication_stats"]
    )

if __name__ == "__main__":
    print(f"🧠 Starting {AGENT_NAME}...")
    print("🏥 Health check available at: GET /health")
    print("📊 Statistics available at: GET /stats")
    print("\n" + "="*60)
    
    orchestrator.run()