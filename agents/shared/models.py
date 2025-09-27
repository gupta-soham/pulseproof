"""
Simplified data models for PulseProof Multi-Agent System
Defines the structure for event data and agent communication
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from uagents import Model


class EventType(str, Enum):
    """Supported event types for blockchain analysis"""
    TRANSFER = "Transfer"
    APPROVAL = "Approval"
    SWAP = "Swap"
    FLASHLOAN = "FlashLoan"
    PERMIT = "Permit"
    UNKNOWN = "Unknown"


class SuspicionLevel(int, Enum):
    """Suspicion levels for risk assessment"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class CandidateEvent(Model):
    """Raw event data received from substream"""
    transaction_hash: str
    block_number: str
    log_index: str
    contract_address: str
    event_signature: str
    event_type: EventType
    metadata: str


class ProcessedEvent(Model):
    """Preprocessed event data with parsed metadata"""
    transaction_hash: str
    block_number: int
    log_index: int
    contract_address: str
    event_signature: str
    event_type: EventType
    topics: List[str] = []
    data: str = "0x"
    parsed_data: Dict[str, Any] = {}
    suspicion_level: SuspicionLevel = SuspicionLevel.LOW
    risk_factors: List[str] = []
    timestamp: Optional[int] = None


class EventAnalysisRequest(Model):
    """Request model for event analysis"""
    events: List[CandidateEvent]
    analysis_type: str = "comprehensive"
    priority: str = "normal"


class AgentStatus(Model):
    """Agent status information"""
    agent_name: str
    agent_address: str
    status: str
    last_activity: Optional[str] = None
    capabilities: List[str] = []


class OrchestratorMessage(Model):
    """Base message model for orchestrator communication"""
    message_type: str
    sender: str
    timestamp: str
    data: Dict[str, Any]


class EventAcknowledgment(Model):
    """Acknowledgment for event processing"""
    request_id: str
    events_received: int
    status: str
    message: str
    processing_started: bool


class EventAnalysisResponse(Model):
    """Response model for event analysis"""
    status: str
    acknowledgment: EventAcknowledgment
    summary: Dict[str, Any]


class HealthResponse(Model):
    """Health check response"""
    status: str
    agent_name: str
    agent_address: str
    uptime_seconds: float
    events_processed: int
    high_risk_events: int
    timestamp: str


class StatsResponse(Model):
    """Statistics response"""
    agent_info: Dict[str, Any]
    processing_stats: Dict[str, Any]
    capabilities: List[str]
    sub_agents: Optional[Dict[str, str]] = None
    delegation_stats: Optional[Dict[str, int]] = None
    agent_health: Optional[Dict[str, str]] = None


class RiskAssessment(Model):
    """Risk assessment result"""
    transaction_hash: str
    risk_score: float
    confidence: float
    risk_category: str
    factors: List[str]
    recommendation: str


class RiskCategory(str, Enum):
    """Risk categories for assessment"""
    FINANCIAL_IMPACT = "financial_impact"
    SECURITY_VULNERABILITY = "security_vulnerability"
    OPERATIONAL_RISK = "operational_risk"
    COMPLIANCE_VIOLATION = "compliance_violation"
    UNKNOWN = "unknown"