"""
Real agent communication models for Phase 2
Following Fetch.ai uAgents communication patterns
"""

from typing import List, Dict, Any, Optional
from uagents import Model
from models import CandidateEvent, ProcessedEvent, SuspicionLevel, EventType

# ============================================================================
# Event Analyzer Agent Communication Models
# ============================================================================

class EventAnalysisRequest(Model):
    """Request for event analysis from Orchestrator to Event Analyzer"""
    candidate_events: List[CandidateEvent]
    request_id: str
    priority: str = "normal"

class EventAnalysisResult(Model):
    """Result from Event Analyzer to Risk Assessor"""
    processed_events: List[ProcessedEvent]
    patterns_detected: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    request_id: str
    processing_time: float
    confidence_score: float

# ============================================================================
# Risk Assessor Agent Communication Models
# ============================================================================

class RiskAssessmentRequest(Model):
    """Request for risk assessment from Orchestrator to Risk Assessor"""
    processed_events: List[ProcessedEvent]
    patterns_detected: List[Dict[str, Any]]
    request_id: str
    priority: str = "normal"

class RiskAssessmentResult(Model):
    """Result from Risk Assessor to Orchestrator"""
    risk_assessments: List[Dict[str, Any]]
    overall_risk_score: float
    critical_events: List[Dict[str, Any]]
    recommendations: List[str]
    request_id: str
    assessment_time: float
    confidence_score: float

# ============================================================================
# Orchestrator Communication Models
# ============================================================================

class OrchestratorRequest(Model):
    """Request from external client to Orchestrator"""
    events: List[CandidateEvent]
    analysis_type: str = "comprehensive"
    priority: str = "normal"

class OrchestratorResponse(Model):
    """Final response from Orchestrator to external client"""
    status: str
    request_id: str
    events_processed: int
    high_risk_events: int
    critical_events: int
    patterns_detected: int
    recommendations: List[str]
    overall_risk_score: float
    processing_time: float
    confidence_score: float
    summary: Dict[str, Any]

# ============================================================================
# Agent Status and Health Models
# ============================================================================

class AgentHealthCheck(Model):
    """Health check request between agents"""
    requester: str
    timestamp: str

class AgentHealthResponse(Model):
    """Health check response"""
    agent_name: str
    agent_address: str
    status: str
    uptime_seconds: float
    events_processed: int
    timestamp: str

class AgentStatusUpdate(Model):
    """Status update between agents"""
    agent_name: str
    status: str
    message: str
    timestamp: str

# ============================================================================
# Error and Acknowledgment Models
# ============================================================================

class AgentError(Model):
    """Error message between agents"""
    error_type: str
    error_message: str
    request_id: str
    agent_name: str
    timestamp: str

class AgentAcknowledgment(Model):
    """Acknowledgment message between agents"""
    request_id: str
    status: str
    message: str
    agent_name: str
    timestamp: str

# ============================================================================
# Workflow Coordination Models
# ============================================================================

class WorkflowStep(Model):
    """Individual workflow step"""
    step_name: str
    status: str  # pending, processing, completed, failed
    agent_name: str
    start_time: str
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WorkflowStatus(Model):
    """Overall workflow status"""
    workflow_id: str
    current_step: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0.0 to 1.0
    steps: List[WorkflowStep]
    estimated_completion: Optional[str] = None
    error_message: Optional[str] = None

# ============================================================================
# Pattern Detection Models
# ============================================================================

class PatternDetectionRequest(Model):
    """Request for pattern detection"""
    processed_events: List[ProcessedEvent]
    request_id: str
    pattern_types: List[str] = []  # specific patterns to detect

class PatternDetectionResult(Model):
    """Result of pattern detection"""
    patterns_detected: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    request_id: str
    processing_time: float

# ============================================================================
# Risk Analysis Models
# ============================================================================

class RiskAnalysisRequest(Model):
    """Request for risk analysis"""
    processed_events: List[ProcessedEvent]
    patterns_detected: List[Dict[str, Any]]
    request_id: str
    analysis_depth: str = "comprehensive"  # basic, comprehensive, deep

class RiskAnalysisResult(Model):
    """Result of risk analysis"""
    risk_assessments: List[Dict[str, Any]]
    overall_risk_score: float
    risk_categories: Dict[str, int]
    critical_events: List[Dict[str, Any]]
    recommendations: List[str]
    request_id: str
    analysis_time: float
    confidence_score: float
