#!/usr/bin/env python3
"""
PulseProof Red Agent - Suspicious Activity Detection & PoC Generation
Receives CandidateEvents from substream and generates exploit PoCs
"""

import asyncio
import logging
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from uagents import Agent, Context
from risk_engine import RiskEngine
from poc_generator import PoCGenerator
from web3 import Web3

# Configure logging
def setup_logging():
    logging.basicConfig(level=logging.INFO)

def load_config():
    return {"host": "0.0.0.0", "port": 8001, "debug": False}

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="PulseProof Red Agent", version="0.1.0")
red_agent = Agent(name="RedDetector", seed="red_seed",port=8000,
    endpoint=["http://localhost:8000/submit"]
)
# Models
class CandidateEvent(BaseModel):
    transaction_hash: str
    block_number: int
    log_index: int
    contract_address: str
    event_signature: str
    event_type: str
    event_name: str  # Legacy field that may still be expected by some API endpoints
    metadata: dict

class CandidateEvents(BaseModel):
    events: List[CandidateEvent]

class PoCRequest(BaseModel):
    event: CandidateEvent
    vulnerability_type: str
    target_contract: str
    attack_vector: str

class PoCResponse(BaseModel):
    poc_id: str
    status: str
    foundry_test_code: str
    description: str
    severity: str
    estimated_impact: float

ALCHEMY_API_KEY="BmBHDMT2RbA9fJNLaN0lm"
# Global components
w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"))  # Using demo endpoint
risk_analyzer = RiskEngine(w3)
poc_generator = PoCGenerator()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "red-agent"}

@app.post("/analyze-events")
async def analyze_events(events: CandidateEvents) -> dict:
    """
    Analyze candidate events and generate PoCs for high-risk activities
    """
    logger.info(f"Received {len(events.events)} candidate events for analysis")
    
    results = []
    processing_start = time.time()
    
    for i, event in enumerate(events.events):
        event_start = time.time()
        try:
            # Simulate realistic analysis time (0.1-0.5s per event)
            analysis_delay = min(0.1 + (len(events.events) * 0.05), 0.5)
            await asyncio.sleep(analysis_delay)
            
            # Risk analysis
            risk_assessment = risk_analyzer.assess_risk(event)
            
            # Generate PoC if risk is significant
            if risk_assessment['should_generate_poc']:
                
                try:
                    poc_response = await poc_generator.generate_poc(event, risk_assessment)
                    # Convert PoCResponse to dict properly
                    poc_dict = {
                        "poc_id": poc_response.poc_id,
                        "status": poc_response.status,
                        "foundry_test_code": poc_response.foundry_test_code,
                        "description": poc_response.description,
                        "severity": poc_response.severity,
                        "estimated_impact": poc_response.estimated_impact,
                        "out_path": poc_response.out_path
                    }
                    results.append({
                        "event_id": f"{event.transaction_hash}_{event.log_index}",
                        "risk_score": risk_assessment['risk_score'],
                        "confidence": risk_assessment.get('confidence', 0.0),
                        "poc_generated": True,
                        "poc": poc_dict
                    })
                except Exception as poc_error:
                    logger.error(f"PoC generation failed for event {event.transaction_hash}: {poc_error}")
                    results.append({
                        "event_id": f"{event.transaction_hash}_{event.log_index}",
                        "risk_score": risk_assessment['risk_score'],
                        "confidence": risk_assessment.get('confidence', 0.0),
                        "poc_generated": False,
                        "reason": f"PoC generation failed: {str(poc_error)}"
                    })
            else:
                results.append({
                    "event_id": f"{event.transaction_hash}_{event.log_index}",
                    "risk_score": risk_assessment['risk_score'],
                    "confidence": risk_assessment.get('confidence', 0.0),
                    "poc_generated": False,
                    "reason": "Risk score below threshold for PoC generation"
                })
                
        except Exception as e:
            logger.error(f"Error analyzing event {event.transaction_hash}: {e}")
            results.append({
                "event_id": f"{event.transaction_hash}_{event.log_index}",
                "risk_score": 0.0,  # Default risk score
                "confidence": 0.0,
                "error": str(e),
                "poc_generated": False
            })
    
    processing_time = time.time() - processing_start
    pocs_generated = sum(1 for r in results if r.get("poc_generated"))
    
    logger.info(f"Analysis complete: {len(results)} events in {processing_time:.2f}s, {pocs_generated} PoCs generated")
    
    return {
        "total_events": len(events.events),
        "analyzed": len(results),
        "pocs_generated": pocs_generated,
        "processing_time": round(processing_time, 2),
        "results": results
    }

@app.get("/stats")
async def get_stats():
    """
    Get Red Agent statistics
    """
    return {
        "events_processed": getattr(risk_analyzer, 'events_processed', 0),
        "pocs_generated": getattr(poc_generator, 'pocs_generated', 0),
        "high_risk_events": getattr(risk_analyzer, 'high_risk_events', 0),
        "uptime": "running"
    }

@app.post("/webhook/substream")
async def substream_webhook(events: CandidateEvents):
    """
    Webhook endpoint for receiving events from substream
    """
    logger.info(f"Webhook received {len(events.events)} events from substream")
    
    # Process in background
    asyncio.create_task(analyze_events(events))
    
    return {"status": "received", "count": len(events.events)}

if __name__ == "__main__":
    config = load_config()
    uvicorn.run(
        "red_agent:app",
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8001),
        reload=config.get("debug", False),
        log_level="info"
    )