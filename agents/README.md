# PulseProof Multi-Agent System

External Client
    ↓ POST /analyze-events
Master Orchestrator
    ↓ ctx.send_and_receive(EventAnalysisRequest)
Event Analyzer
    ↓ ctx.send(EventAnalysisResult)
Master Orchestrator
    ↓ ctx.send_and_receive(RiskAssessmentRequest)
Risk Assessor
    ↓ ctx.send(RiskAssessmentResult)
Master Orchestrator
    ↓ Final EventAnalysisResponse
External Client


## Master Orchestrator
- Orchestrator: Coordinates the flow and synthesizes final results
- Event Analyzer: Takes raw events → Preprocesses → Detects patterns → Sends structured data
- Risk Assessor: Takes structured data → Analyzes risk → Generates recommendations → Sends risk assessment
