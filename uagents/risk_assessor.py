# AGENTVERSE ADDRESS - agent1qwrpjgfc8ypwvk05ufd63q7tj7psgwf35djh8wpzrzm2jruvsznugjj0k54

class EventAnalysisResult(Model):
    """Response from Event Analyzer to Master Orchestrator"""
    request_id: str
    event_type: str
    contract_address: str
    transaction_hash: str
    analysis: str
    anomaly_detected: bool


class RiskAssessmentRequest(Model):
    """Request sent from Master Orchestrator to Risk Assessor"""
    event_analysis: EventAnalysisResult
    request_id: str


class RiskAssessmentResult(Model):
    """Response from Risk Assessor to Master Orchestrator"""
    request_id: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    risk_score: float  # 0.0 to 1.0
    risk_factors: list[str]
    recommendation: str

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info(f"Risk Assessor started with address: {ctx.agent.address}")


@agent.on_message(model=RiskAssessmentRequest)
async def handle_risk_assessment(ctx: Context, sender: str, msg: RiskAssessmentRequest):
    """Handle risk assessment request from Master Orchestrator"""
    ctx.logger.info(f"Received risk assessment request from {sender} for request: {msg.request_id}")
    
    try:
        # Basic risk assessment logic
        risk_factors = []
        risk_score = 0.1  # Base risk score
        
        # Analyze the event analysis result
        event_analysis = msg.event_analysis
        
        # Check for anomalies
        if event_analysis.anomaly_detected:
            risk_factors.append("Anomaly detected in event analysis")
            risk_score += 0.4
        
        # Check event type
        if event_analysis.event_type == "Transfer":
            risk_factors.append("Transfer event detected")
            risk_score += 0.2
        
        # Check contract address patterns (basic heuristics)
        if len(event_analysis.contract_address) != 42:
            risk_factors.append("Invalid contract address format")
            risk_score += 0.3
        
        # Normalize risk score to 0-1 range
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "LOW"
            recommendation = "Event appears normal, minimal risk detected"
        elif risk_score < 0.7:
            risk_level = "MEDIUM"
            recommendation = "Moderate risk detected, monitor closely"
        else:
            risk_level = "HIGH"
            recommendation = "High risk detected, immediate attention required"
        
        # Create risk assessment result
        result = RiskAssessmentResult(
            request_id=msg.request_id,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            recommendation=recommendation
        )
        
        # Send result back to sender
        await ctx.send(sender, result)
        ctx.logger.info(f"Sent risk assessment result for request {msg.request_id} - Risk Level: {risk_level}")
        
    except Exception as e:
        ctx.logger.error(f"Error in risk assessment: {e}")
        # Send error response
        error_result = RiskAssessmentResult(
            request_id=msg.request_id,
            risk_level="ERROR",
            risk_score=0.0,
            risk_factors=[f"Error in assessment: {str(e)}"],
            recommendation="Unable to assess risk due to error"
        )
        await ctx.send(sender, error_result)
