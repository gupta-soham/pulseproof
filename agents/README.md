# PulseProof Multi-Agent System

External Client <br>
    ↓ POST /analyze-events <br>
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

## Master Orchestrator
- Master Orchestrator: Coordinates the flow and synthesizes final results
- Event Analyzer: Takes raw events → Preprocesses → Detects patterns → Sends structured data
- Risk Assessor: Takes structured data → Analyzes risk → Generates recommendations → Sends risk assessment


## How to run

```$ cd /Users/admin/Downloads/PulseProof/agents && ./manage_phase2_agents.sh status```

```$ cd /Users/admin/Downloads/PulseProof/agents && ./manage_phase2_agents.sh start```

