# PulseProof Multi-Agent System

External Client <br>
    ↓ POST /analyze-events OR ASI ONE CHAT <br>
<b>Master Orchestrator</b> <br>
    ↓ ctx.send_and_receive(EventAnalysisRequest) <br>
<b> Event Analyzer </b> <br>
    ↓ ctx.send(EventAnalysisResult) <br>
<b> Master Orchestrator </b> <br>
    ↓ ctx.send_and_receive(RiskAssessmentRequest) <br>
<b> Risk Assessor </b> <br>
    ↓ ctx.send(RiskAssessmentResult) <br>
<b> Master Orchestrator </b> <br>
    ↓ Final EventAnalysisResponse <br>
External Client <br>
    ↓ POST /generate-poc OR ASI ONE CHAT <br>
<b>POC Generator (with MeTTa)</b> <br>

## Agents
- Master Orchestrator: Coordinates the flow and synthesizes final results
- Event Analyzer: Takes raw events → Preprocesses → Detects patterns → Sends structured data
- Risk Assessor: Takes structured data → Analyzes risk → Generates recommendations → Sends risk assessment
- POC Generator: Generates POC for risk events to help reduce dwell time and minimze loss uses MeTTa Knowledge and structured reasoning
