"""
ASI:One Enhanced Master Orchestrator Agent
- Runs locally with mailbox connectivity
- Communicates with hosted Agentverse agents (Event Analyzer & Risk Assessor)
- Provides REST API for external clients
- Supports ASI:One Chat Protocol for LLM interactions
- Dual interface: REST + Chat Protocol (non-disruptive integration)
- Integrated with ASI:One LLM for natural language responses
"""
from datetime import datetime, UTC
from uuid import uuid4
import time
import json
import re
import os
from typing import Optional, Dict, Any

from openai import OpenAI
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

from models import (
    EventInput, 
    EventAnalysisRequest, 
    EventAnalysisResult,
    RiskAssessmentRequest, 
    RiskAssessmentResult,
    EventAnalysisResponse,
    POCRequest,
    POCResult
)
from config import AGENT_SEEDS, AGENT_PORTS, HOSTED_AGENT_ADDRESSES, AGENT_COMMUNICATION_TIMEOUT

# ASI:One OpenAI Client Configuration
ASI_ONE_API_KEY = os.getenv("ASI_ONE_API_KEY")

client = OpenAI(
    # ASI:One LLM endpoint 
    base_url='https://api.asi1.ai/v1',
    # Get API key from https://asi1.ai/dashboard/api-keys
    api_key=ASI_ONE_API_KEY,
)

# Create ASI:One Enhanced Master Orchestrator Agent (Local with Mailbox)
master_orchestrator = Agent(
    name="asi_one_master_orchestrator",
    port=8010,
    seed="asi_one_master_orchestrator_secret_seed",
    mailbox=True,  # Enables communication with hosted Agentverse agents
    publish_agent_details=True  # Required for ASI:One discovery
)

# Create Chat Protocol for ASI:One compatibility
chat_protocol = Protocol(spec=chat_protocol_spec)


# === CORE ANALYSIS WORKFLOW (Shared by REST and Chat) ===

async def process_blockchain_event(ctx: Context, event_input: EventInput, request_source: str = "REST") -> EventAnalysisResponse:
    """
    Core analysis workflow shared by both REST API and Chat Protocol
    This function encapsulates the existing analysis pipeline
    """
    start_time = time.time()
    request_id = str(uuid4())
    
    ctx.logger.info(f"📨 Processing blockchain event via {request_source} for transaction: {event_input.transactionHash}")
    
    try:
        # Step 1: Send event to hosted Event Analyzer
        ctx.logger.info(f"🔍 Sending event analysis request to hosted Event Analyzer...")
        
        analysis_request = EventAnalysisRequest(
            event=event_input,
            request_id=request_id
        )
        
        # Get hosted event analyzer address
        event_analyzer_addr = HOSTED_AGENT_ADDRESSES["event_analyzer"]
        
        try:
            # Send and receive response from hosted Event Analyzer
            analysis_response, status = await ctx.send_and_receive(
                event_analyzer_addr, 
                analysis_request,
                response_type=EventAnalysisResult,
                timeout=AGENT_COMMUNICATION_TIMEOUT
            )
            
            if not isinstance(analysis_response, EventAnalysisResult):
                raise Exception(f"Failed to get analysis response: {status}")
                
            ctx.logger.info(f"✅ Received analysis result from hosted Event Analyzer")
            
        except Exception as e:
            ctx.logger.warning(f"⚠️  Communication with hosted Event Analyzer failed: {e}")
            ctx.logger.info("🔄 Using fallback analysis")
            # Fallback analysis
            analysis_response = EventAnalysisResult(
                request_id=request_id,
                event_type=event_input.eventType,
                contract_address=event_input.contractAddress,
                transaction_hash=event_input.transactionHash,
                analysis=f"Fallback analysis for {event_input.eventType} event (hosted agent unavailable)",
                anomaly_detected=False
            )
        
        # Step 2: Send analysis result to hosted Risk Assessor
        ctx.logger.info(f"⚖️  Sending risk assessment request to hosted Risk Assessor...")
        
        risk_request = RiskAssessmentRequest(
            event_analysis=analysis_response,
            request_id=request_id
        )
        
        # Get hosted risk assessor address  
        risk_assessor_addr = HOSTED_AGENT_ADDRESSES["risk_assessor"]
        
        try:
            # Send and receive response from hosted Risk Assessor
            risk_response, status = await ctx.send_and_receive(
                risk_assessor_addr,
                risk_request,
                response_type=RiskAssessmentResult,
                timeout=AGENT_COMMUNICATION_TIMEOUT
            )
            
            if not isinstance(risk_response, RiskAssessmentResult):
                raise Exception(f"Failed to get risk assessment response: {status}")
                
            ctx.logger.info(f"✅ Received risk assessment result from hosted Risk Assessor")
            
        except Exception as e:
            ctx.logger.warning(f"⚠️  Communication with hosted Risk Assessor failed: {e}")
            ctx.logger.info("🔄 Using fallback risk assessment")
            # Fallback risk assessment
            risk_response = RiskAssessmentResult(
                request_id=request_id,
                risk_level="MEDIUM",
                risk_score=0.5,
                risk_factors=["Fallback assessment - hosted agent unavailable"],
                recommendation="Unable to perform full risk assessment"
            )
        
        # Step 3: Compile final response
        processing_time = int((time.time() - start_time) * 1000)
        
        response = EventAnalysisResponse(
            transaction_hash=event_input.transactionHash,
            event_analysis={
                "event_type": analysis_response.event_type,
                "contract_address": analysis_response.contract_address,
                "analysis": analysis_response.analysis,
                "anomaly_detected": analysis_response.anomaly_detected
            },
            risk_assessment={
                "risk_level": risk_response.risk_level,
                "risk_score": risk_response.risk_score,
                "risk_factors": risk_response.risk_factors,
                "recommendation": risk_response.recommendation
            },
            overall_status="SUCCESS",
            processing_time_ms=processing_time
        )
        
        ctx.logger.info(f"🎉 Analysis complete for transaction {event_input.transactionHash} via {request_source} in {processing_time}ms")
        return response
        
    except Exception as e:
        ctx.logger.error(f"❌ Error processing event analysis via {request_source}: {e}")
        processing_time = int((time.time() - start_time) * 1000)
        
        return EventAnalysisResponse(
            transaction_hash=event_input.transactionHash,
            event_analysis={"error": f"Failed to analyze event: {str(e)}"},
            risk_assessment={"error": "Risk assessment not performed due to analysis failure"},
            overall_status="ERROR",
            processing_time_ms=processing_time
        )


# === REST API ENDPOINT (Existing Functionality - Unchanged) ===

@master_orchestrator.on_rest_post("/analyze-events", EventInput, EventAnalysisResponse)
async def handle_analyze_events_rest(ctx: Context, req: EventInput) -> EventAnalysisResponse:
    """
    Original REST API endpoint - functionality preserved unchanged
    """
    return await process_blockchain_event(ctx, req, "REST API")


# === ASI:ONE CHAT PROTOCOL INTEGRATION ===

def parse_blockchain_event_from_text(text: str) -> Optional[EventInput]:
    """
    Parse blockchain event data from natural language or structured text
    Supports both JSON format and natural language descriptions
    """
    try:
        # Try to parse as JSON first
        if '{' in text and '}' in text:
            # Extract JSON from text
            json_match = re.search(r'\{[^{}]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                event_data = json.loads(json_str)
                
                # Create EventInput from parsed JSON
                return EventInput(
                    transactionHash=event_data.get("transactionHash", "0x" + "0"*64),
                    blockNumber=event_data.get("blockNumber", "0"),
                    logIndex=event_data.get("logIndex", "0"),
                    contractAddress=event_data.get("contractAddress", "0x" + "0"*40),
                    eventSignature=event_data.get("eventSignature", "0x" + "0"*64),
                    eventType=event_data.get("eventType", "Unknown"),
                    metadata=event_data.get("metadata", "{}")
                )
        
        # If no JSON found, create a sample event for demonstration
        # In production, you'd implement NLP to extract event details
        return EventInput(
            transactionHash="0x" + "sample" + "0"*58,
            blockNumber="1000000",
            logIndex="0",
            contractAddress="0x" + "demo" + "0"*36,
            eventSignature="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            eventType="Transfer",
            metadata='{"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],"data":"0x1000"}'
        )
        
    except Exception as e:
        return None


# === ASI:ONE TOOL CALLING INTEGRATION ===

def get_blockchain_analysis_tool():
    """
    Define the blockchain analysis tool for ASI:One LLM
    Based on official ASI:One tool calling documentation
    """
    return {
        "type": "function",
        "function": {
            "name": "analyze_blockchain_event",
            "description": "Analyze a blockchain event for security risks and anomalies. Use this when users provide blockchain transaction data or ask for event analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transactionHash": {
                        "type": "string",
                        "description": "The blockchain transaction hash (0x followed by 64 hex characters)"
                    },
                    "eventType": {
                        "type": "string", 
                        "description": "Type of blockchain event (e.g., Transfer, Approval, Swap)"
                    },
                    "contractAddress": {
                        "type": "string",
                        "description": "Smart contract address (0x followed by 40 hex characters)"
                    },
                    "blockNumber": {
                        "type": "string",
                        "description": "Block number where the event occurred"
                    },
                    "logIndex": {
                        "type": "string", 
                        "description": "Log index within the block"
                    },
                    "eventSignature": {
                        "type": "string",
                        "description": "Event signature hash"
                    },
                    "metadata": {
                        "type": "string",
                        "description": "Event metadata as JSON string containing topics and data"
                    }
                },
                "required": ["transactionHash", "eventType", "contractAddress"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

async def execute_blockchain_analysis_tool(parameters: dict, ctx: Context) -> dict:
    """
    Execute the blockchain analysis tool by calling hosted agents
    Returns results that will be sent back to ASI:One LLM
    """
    try:
        ctx.logger.info("🛠️ TOOL EXECUTION: analyze_blockchain_event called")
        ctx.logger.info(f"📊 Parameters: {parameters}")
        
        # Create EventInput from tool parameters
        event_input = EventInput(
            transactionHash=parameters.get("transactionHash", ""),
            blockNumber=parameters.get("blockNumber", "0"),
            logIndex=parameters.get("logIndex", "0"),
            contractAddress=parameters.get("contractAddress", ""),
            eventSignature=parameters.get("eventSignature", "0x0"),
            eventType=parameters.get("eventType", "Unknown"),
            metadata=parameters.get("metadata", "{}")
        )
        
        ctx.logger.info(f"🚀 Executing REAL blockchain analysis via hosted agents...")
        
        # Use existing analysis workflow with hosted agents
        analysis_response = await process_blockchain_event(ctx, event_input, "ASI:One Tool")
        
        # Format results for ASI:One LLM
        tool_result = {
            "status": "success",
            "transaction_hash": analysis_response.transaction_hash,
            "event_analysis": analysis_response.event_analysis,
            "risk_assessment": analysis_response.risk_assessment,
            "overall_status": analysis_response.overall_status,
            "processing_time_ms": analysis_response.processing_time_ms,
            "analysis_source": "hosted_agents_via_agentverse"
        }
        
        ctx.logger.info("✅ TOOL SUCCESS: Real blockchain analysis completed")
        return tool_result
        
    except Exception as e:
        ctx.logger.error(f"❌ TOOL ERROR: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "analysis_source": "tool_execution_failed"
        }


def get_poc_generator_tool():
    """
    Define the POC generator tool for ASI:One LLM
    Enables natural language POC generation with MeTTa reasoning
    """
    return {
        "type": "function",
        "function": {
            "name": "generate_poc",
            "description": "Generate a proof of concept for blockchain/DeFi/security projects using MeTTa structured reasoning. Use this tool when users ask to 'generate POC', 'create POC', 'build POC', or 'POC for this event'. Can create security monitoring systems, risk dashboards, and threat detection solutions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Project requirements and goals. For event-based POCs, describe the security solution needed (e.g., 'Transfer event monitoring system', 'DeFi risk dashboard', 'suspicious transaction detector')"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Project domain based on context: 'defi' for DeFi/token events, 'nft' for NFT events, 'security' for general security monitoring, 'blockchain' for other blockchain events"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about the specific event, threat, or use case that triggered the POC request",
                        "default": ""
                    }
                },
                "required": ["requirements", "domain"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

async def execute_poc_generator_tool(parameters: dict, ctx: Context) -> dict:
    """
    Execute the POC generator tool by calling hosted POC Generator agent
    Returns POC results that will be sent back to ASI:One LLM
    """
    try:
        ctx.logger.info("🛠️ TOOL EXECUTION: generate_poc called")
        ctx.logger.info(f"📋 Parameters: {parameters}")
        
        # Enhanced requirements processing for event-based POCs
        requirements = parameters.get("requirements", "")
        domain = parameters.get("domain", "blockchain")
        context = parameters.get("context", "")
        
        # If context suggests this is event-based, enhance requirements
        if "transfer" in requirements.lower() or "event" in context.lower():
            if domain == "defi":
                requirements = f"DeFi Transfer event monitoring and risk assessment system - {requirements}"
            elif domain == "security":
                requirements = f"Blockchain security monitoring system for suspicious events - {requirements}"
            else:
                requirements = f"Blockchain event monitoring and analysis system - {requirements}"
        
        # Infer risk factors from context
        risk_factors = []
        if "suspicious" in context.lower() or "anomaly" in context.lower():
            risk_factors.append("anomaly_detected")
        if "transfer" in requirements.lower():
            risk_factors.append("high_value_transfer")
        
        # Create POC request from tool parameters
        poc_request = POCRequest(
            requirements=requirements,
            domain=domain,
            risk_factors=risk_factors,
            event_context=None,  # Could be enhanced with actual EventAnalysisResult
            request_id=str(uuid4())
        )
        
        ctx.logger.info(f"🚀 Executing POC generation via hosted agent...")
        
        # Get hosted POC generator address
        poc_generator_addr = HOSTED_AGENT_ADDRESSES["poc_generator"]
        
        # Send and receive response from hosted POC Generator
        poc_response, status = await ctx.send_and_receive(
            poc_generator_addr,
            poc_request,
            response_type=POCResult,
            timeout=AGENT_COMMUNICATION_TIMEOUT
        )
        
        if not isinstance(poc_response, POCResult):
            raise Exception(f"Failed to get POC response: {status}")
        
        # Format results for ASI:One LLM
        tool_result = {
            "status": "success",
            "poc_title": poc_response.poc_title,
            "architecture": poc_response.architecture,
            "implementation_steps": poc_response.implementation_steps,
            "code_snippet": poc_response.code_snippet,
            "metta_reasoning": poc_response.metta_reasoning,
            "threat_addressed": poc_response.threat_addressed,
            "integration_notes": poc_response.integration_notes,
            "generation_source": "metta_knowledge_graph_with_asi_one"
        }
        
        ctx.logger.info("✅ TOOL SUCCESS: POC generation completed")
        return tool_result
        
    except Exception as e:
        ctx.logger.error(f"❌ POC TOOL ERROR: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "fallback_suggestion": "Please try a more specific POC request with clear domain (defi/nft/security/blockchain) and requirements",
            "generation_source": "tool_execution_failed"
        }


async def generate_asi_one_response_with_tools(user_message: str, ctx: Context) -> str:
    """
    Generate response using ASI:One LLM with tool calling capability
    This replaces the old generate_asi_one_response function
    """
    try:
        ctx.logger.info("🧠 Generating ASI:One response WITH tool calling...")
        
        # System prompt for blockchain security expert with tools
        system_prompt = """You are a blockchain security expert agent that specializes in analyzing blockchain events and generating security solutions.

**TOOL SELECTION RULES:**
1. **When user asks to "generate POC", "create POC", or "build POC"** → ALWAYS use generate_poc tool
2. **When user provides event data for analysis** → use analyze_blockchain_event tool
3. **When user asks to "generate POC for this event"** → use generate_poc tool (infer requirements from event context)

**Your Capabilities:**

🔍 **Blockchain Analysis (analyze_blockchain_event tool):**
- Use when users ask to "analyze this event" or "check this transaction"
- Transfer events, Approval events, smart contract interactions
- DeFi protocols, NFT marketplaces, bridges
- Risk assessment and anomaly detection

🎯 **POC Generation (generate_poc tool):**
- Use when users ask to "generate POC", "create POC", "build POC"
- Use when users ask for "POC for this event" (use event as context)
- Architecture recommendations and security system designs
- Monitoring dashboards and risk assessment systems
- DeFi security solutions and NFT authenticity systems

**POC Generation Keywords (ALWAYS use generate_poc tool):**
- "generate POC"
- "create POC" 
- "build POC"
- "POC for"
- "proof of concept"
- "architecture for"
- "system to monitor"
- "dashboard for"

**Analysis Keywords (use analyze_blockchain_event tool):**
- "analyze this event"
- "check this transaction"
- "assess the risk"
- "is this suspicious"

Always choose the correct tool based on these keywords. When in doubt about POC generation, use the generate_poc tool."""

        # First call to ASI:One with tools
        initial_response = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=[get_blockchain_analysis_tool(), get_poc_generator_tool()],
            tool_choice="auto",  # Let ASI:One decide when to use tools
            temperature=0.7,
            max_tokens=1500
        )
        
        # Check if ASI:One wants to call tools
        choice = initial_response.choices[0]
        
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            ctx.logger.info(f"🛠️ ASI:One requested {len(choice.message.tool_calls)} tool call(s)")
            
            # Prepare message history for tool results
            messages_history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {
                    "role": "assistant", 
                    "content": choice.message.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in choice.message.tool_calls
                    ]
                }
            ]
            
            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                ctx.logger.info(f"🔧 Executing tool: {tool_call.function.name}")
                
                try:
                    # Parse tool arguments
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Execute the appropriate tool
                    if tool_call.function.name == "analyze_blockchain_event":
                        tool_result = await execute_blockchain_analysis_tool(arguments, ctx)
                    elif tool_call.function.name == "generate_poc":
                        tool_result = await execute_poc_generator_tool(arguments, ctx)
                    else:
                        tool_result = {"status": "error", "error_message": f"Unknown tool: {tool_call.function.name}"}
                    
                    # Add tool result to message history
                    messages_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
                    
                    ctx.logger.info(f"✅ Tool execution complete: {tool_call.function.name}")
                    
                except Exception as e:
                    ctx.logger.error(f"❌ Tool execution failed: {e}")
                    # Send error as tool result
                    error_result = {
                        "status": "error",
                        "error_message": f"Tool execution failed: {str(e)}"
                    }
                    messages_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(error_result)
                    })
            
            # Second call to ASI:One with tool results
            ctx.logger.info("🧠 Sending tool results back to ASI:One for final response...")
            final_response = client.chat.completions.create(
                model="asi1-mini",
                messages=messages_history,
                temperature=0.7,
                max_tokens=1500
            )
            
            final_answer = final_response.choices[0].message.content
            ctx.logger.info("✅ ASI:One generated final response with tool results")
            return final_answer
            
        else:
            # No tools needed, return direct response
            ctx.logger.info("💬 No tools needed, returning direct ASI:One response")
            return choice.message.content or "I'm ready to help with blockchain analysis!"
        
    except Exception as e:
        ctx.logger.error(f"❌ ASI:One API error: {e}")
        
        # Fallback response
        return f"""⚠️ I'm experiencing technical difficulties with my analysis tools, but I'm here to help with blockchain security analysis.

Please provide blockchain event data in this format:
```json
{{
  "transactionHash": "0x123...",
  "eventType": "Transfer",
  "contractAddress": "0xabc...",
  "blockNumber": "12345",
  "logIndex": "0",
  "eventSignature": "0xdef...",
  "metadata": "{{\\"topics\\":[...],\\"data\\":\\"0x...\\"}}"
}}
```

What blockchain event would you like me to analyze?

Error details: {str(e)}"""


def format_analysis_for_chat_fallback(response: EventAnalysisResponse) -> str:
    """
    Convert EventAnalysisResponse to human-readable chat format
    """
    if response.overall_status == "ERROR":
        return "❌ I encountered an error while analyzing the blockchain event. Please check your event data and try again."
    
    analysis = response.event_analysis
    risk = response.risk_assessment
    
    # Format response for natural language interaction
    chat_response = f"""🔍 **Blockchain Event Analysis Complete**

**Transaction**: `{response.transaction_hash}`

**Event Analysis**:
• **Type**: {analysis.get('event_type', 'Unknown')}
• **Contract**: `{analysis.get('contract_address', 'N/A')}`
• **Analysis**: {analysis.get('analysis', 'No analysis available')}
• **Anomaly Detected**: {'⚠️ Yes' if analysis.get('anomaly_detected') else '✅ No'}

**Risk Assessment**:
• **Risk Level**: {risk.get('risk_level', 'Unknown')} 
• **Risk Score**: {risk.get('risk_score', 0):.1%}
• **Risk Factors**: {', '.join(risk.get('risk_factors', []))}
• **Recommendation**: {risk.get('recommendation', 'No recommendation available')}

**Processing Time**: {response.processing_time_ms}ms

Is there anything specific about this blockchain event you'd like me to explain further?"""

    return chat_response


# === CHAT PROTOCOL MESSAGE HANDLERS ===

@chat_protocol.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle chat messages from ASI:One or other agents
    Enhanced with ASI:One LLM integration and detailed logging
    """
    message_start_time = time.time()
    
    # Send acknowledgement for receiving the message
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(UTC), acknowledged_msg_id=msg.msg_id),
    )
    
    # Collect all text content from the message
    text = ''
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text + ' '
    
    text = text.strip()
    
    # Enhanced logging
    ctx.logger.info(f"💬 CHAT REQUEST from {sender[:20]}...")
    ctx.logger.info(f"📝 Message ID: {msg.msg_id}")
    ctx.logger.info(f"📝 Message content: {text[:200]}{'...' if len(text) > 200 else ''}")
    ctx.logger.info(f"📅 Message timestamp: {msg.timestamp}")
    
    try:
        # Use ASI:One with tool calling - let the LLM decide what to do
        ctx.logger.info("🧠 Using ASI:One LLM with tool calling capability...")
        
        # Generate response using ASI:One with tool calling
        chat_response = await generate_asi_one_response_with_tools(
            user_message=text,
            ctx=ctx
        )
    
    except Exception as e:
        ctx.logger.error(f"❌ Error processing chat message: {e}")
        chat_response = "⚠️ I encountered an error processing your request. Please try again or provide blockchain event data in JSON format."
    
    # Smart session management
    # End session if response suggests completion, otherwise keep open for follow-ups
    session_indicators = ["analysis complete", "assessment finished", "results show", "final verdict"]
    should_end_session = any(indicator in chat_response.lower() for indicator in session_indicators)
    
    message_content = [TextContent(type="text", text=chat_response)]
    
    # Add EndSessionContent for completed analysis or very long responses
    if should_end_session or len(chat_response) > 2000:
        message_content.append(EndSessionContent(type="end-session"))
        ctx.logger.info("🔚 Ending session after analysis completion")
    else:
        ctx.logger.info("💭 Keeping session open for follow-up questions")
    
    processing_time = int((time.time() - message_start_time) * 1000)
    
    # Enhanced response logging
    ctx.logger.info(f"📤 SENDING RESPONSE to {sender[:20]}...")
    ctx.logger.info(f"📝 Response length: {len(chat_response)} characters")
    ctx.logger.info(f"📝 Response preview: {chat_response[:150]}{'...' if len(chat_response) > 150 else ''}")
    ctx.logger.info(f"⏱️ Chat processing time: {processing_time}ms")
    
    try:
        # Send the response back to the user
        response_msg = ChatMessage(
            timestamp=datetime.now(UTC),
            msg_id=uuid4(),
            content=message_content
        )
        
        await ctx.send(sender, response_msg)
        
        ctx.logger.info("✅ Chat response sent successfully")
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to send chat response: {e}")
        ctx.logger.error(f"❌ Sender: {sender}")
        ctx.logger.error(f"❌ Response length: {len(chat_response)}")
        
        # Try to send a simpler error message
        try:
            error_response = ChatMessage(
                timestamp=datetime.now(UTC),
                msg_id=uuid4(),
                content=[
                    TextContent(type="text", text="⚠️ Error sending response. Please try again."),
                    EndSessionContent(type="end-session")
                ]
            )
            await ctx.send(sender, error_response)
            ctx.logger.info("✅ Error response sent successfully")
        except Exception as e2:
            ctx.logger.error(f"❌ Failed to send error response: {e2}")


@chat_protocol.on_message(ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """
    Handle chat acknowledgements (for read receipts, etc.)
    Enhanced with detailed logging
    """
    ctx.logger.info(f"📨 ACKNOWLEDGEMENT from {sender[:20]}...")
    ctx.logger.info(f"📝 Acknowledged message ID: {msg.acknowledged_msg_id}")
    ctx.logger.info(f"📅 Acknowledgement timestamp: {msg.timestamp}")
    ctx.logger.debug(f"🔍 Full sender address: {sender}")


# === AGENT STARTUP AND PROTOCOL ATTACHMENT ===

@master_orchestrator.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info(f"🌐 ASI:One Enhanced Master Orchestrator started")
    ctx.logger.info(f"📍 Local address: {ctx.agent.address}")
    ctx.logger.info(f"🤖 Event Analyzer (Hosted): {HOSTED_AGENT_ADDRESSES['event_analyzer']}")
    ctx.logger.info(f"⚖️  Risk Assessor (Hosted): {HOSTED_AGENT_ADDRESSES['risk_assessor']}")
    ctx.logger.info(f"🎯 POC Generator (Hosted): {HOSTED_AGENT_ADDRESSES['poc_generator'][:20]}...")
    ctx.logger.info(f"🧠 ASI:One API Status: {'✅ Configured' if ASI_ONE_API_KEY != 'your_asi_one_api_key_here' else '⚠️ API Key needed'}")
    ctx.logger.info("🚀 Ready for:")
    ctx.logger.info("   • REST API requests via /analyze-events")
    ctx.logger.info("   • ASI:One Chat Protocol with dual tool calling")
    ctx.logger.info("   • Blockchain analysis via Event Analyzer + Risk Assessor")
    ctx.logger.info("   • POC generation via MeTTa knowledge graph reasoning")
    ctx.logger.info("   • Natural language processing with real data")
    ctx.logger.info("   • Enhanced logging and error handling")


# Attach the chat protocol to the agent
master_orchestrator.include(chat_protocol, publish_manifest=True)


if __name__ == "__main__":
    print("🌐 Starting ASI:One Enhanced Master Orchestrator")
    print("=" * 70)
    print("🔄 Dual Interface Architecture:")
    print("   • REST API: /analyze-events (existing functionality)")
    print("   • Chat Protocol: ASI:One with intelligent tool calling")
    print("   • ASI:One LLM: Natural language processing + tools")
    print("=" * 70)
    print("🌍 Architecture: Local Mailbox Agent + Hosted Agentverse Agents")
    print(f"🌐 REST API: http://localhost:8010/analyze-events")
    print(f"💬 Chat Protocol: ASI:One powered with tool calling")
    print(f"🧠 ASI:One API: {'✅ Configured' if ASI_ONE_API_KEY != 'your_asi_one_api_key_here' else '⚠️ Set ASI_ONE_API_KEY env var'}")
    print(f"🤖 Event Analyzer: {HOSTED_AGENT_ADDRESSES['event_analyzer'][:20]}...")
    print(f"⚖️  Risk Assessor: {HOSTED_AGENT_ADDRESSES['risk_assessor'][:20]}...")
    print("=" * 70)
    print("🚀 Features:")
    print("   • ASI:One LLM with tool calling capability")
    print("   • Intelligent blockchain analysis via hosted agents")
    print("   • Natural language responses with REAL data")
    print("   • Smart session management")
    print("   • Enhanced logging and debugging")
    print("=" * 70)
    
    if ASI_ONE_API_KEY == "your_asi_one_api_key_here":
        print("⚠️  WARNING: Set your ASI:One API key as environment variable:")
        print("   export ASI_ONE_API_KEY='your_actual_api_key'")
        print("   Get API key from: https://asi1.ai/dashboard/api-keys")
        print("=" * 70)
    
    master_orchestrator.run()
