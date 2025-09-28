# AGENTVERSE ADDRESS: agent1qfzgj4ks8wkh5nnhjagkdcw3hdwcehcu4a0vjvgxvlwsy784yxxk5sxw8td

from uagents import Agent, Context, Model

class EventInput(Model):
    """Input event schema matching the client's POST request"""
    transactionHash: str
    blockNumber: str
    logIndex: str
    contractAddress: str
    eventSignature: str
    eventType: str
    metadata: str


class EventAnalysisRequest(Model):
    """Request sent from Master Orchestrator to Event Analyzer"""
    event: EventInput
    request_id: str


class EventAnalysisResult(Model):
    """Response from Event Analyzer to Master Orchestrator"""
    request_id: str
    event_type: str
    contract_address: str
    transaction_hash: str
    analysis: str
    anomaly_detected: bool

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info(f"Event Analyzer started with address: {ctx.agent.address}")


@agent.on_message(model=EventAnalysisRequest)
async def handle_event_analysis(ctx: Context, sender: str, msg: EventAnalysisRequest):
    """Handle event analysis request from Master Orchestrator"""
    ctx.logger.info(f"Received event analysis request from {sender} for transaction: {msg.event.transactionHash}")
    
    # Basic event analysis logic
    try:
        # Parse metadata if it's JSON
        metadata = {}
        try:
            metadata = json.loads(msg.event.metadata)
        except:
            ctx.logger.warning("Failed to parse event metadata as JSON")
        
        # Simple analysis logic
        anomaly_detected = False
        analysis = f"Analyzed {msg.event.eventType} event on contract {msg.event.contractAddress}"
        
        # Check for potential anomalies
        if msg.event.eventType == "Transfer":
            # Basic transfer analysis
            topics = metadata.get("topics", [])
            if len(topics) >= 3:
                analysis += f" - Transfer detected with {len(topics)} topics"
            anomaly_detected = len(topics) > 4  # Simple anomaly detection
        
        # Create response
        result = EventAnalysisResult(
            request_id=msg.request_id,
            event_type=msg.event.eventType,
            contract_address=msg.event.contractAddress,
            transaction_hash=msg.event.transactionHash,
            analysis=analysis,
            anomaly_detected=anomaly_detected
        )
        
        # Send result back to sender
        await ctx.send(sender, result)
        ctx.logger.info(f"Sent event analysis result for request {msg.request_id}")
        
    except Exception as e:
        ctx.logger.error(f"Error analyzing event: {e}")
        # Send error response
        error_result = EventAnalysisResult(
            request_id=msg.request_id,
            event_type=msg.event.eventType,
            contract_address=msg.event.contractAddress,
            transaction_hash=msg.event.transactionHash,
            analysis=f"Error in analysis: {str(e)}",
            anomaly_detected=False
        )
        await ctx.send(sender, error_result)
