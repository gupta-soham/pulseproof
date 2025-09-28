from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict
import json
import os
from dotenv import load_dotenv
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from metta.investment_rag import POCRAG
from metta.knowledge import initialize_poc_knowledge
from metta.utils import LLM, process_poc_query

# Import models from the main models.py to ensure schema consistency
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import POCRequest, POCResult

load_dotenv()

agent = Agent(name="POC Generator Agent", port=8009, mailbox=True, publish_agent_details=True)

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )

# Initialize MeTTa knowledge graph for POC generation
metta = MeTTa()
initialize_poc_knowledge(metta)
poc_rag = POCRAG(metta)
llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))

# Chat protocol for testing via Agentverse
chat_proto = Protocol(spec=chat_protocol_spec)

@agent.on_message(model=POCRequest)
async def handle_poc_request(ctx: Context, sender: str, msg: POCRequest):
    """Handle POC generation request from Master Orchestrator"""
    ctx.logger.info(f"🎯 Received POC generation request from {sender}")
    ctx.logger.info(f"📋 Requirements: {msg.requirements}")
    ctx.logger.info(f"🏷️ Domain: {msg.domain}")
    ctx.logger.info(f"⚠️ Risk factors: {msg.risk_factors}")
    
    try:
        # Use MeTTa knowledge graph to generate POC
        poc_data = process_poc_query(
            requirements=msg.requirements,
            domain=msg.domain,
            risk_factors=msg.risk_factors,
            rag=poc_rag,
            llm=llm
        )
        
        # Create POC result
        result = POCResult(
            request_id=msg.request_id,
            poc_title=poc_data["title"],
            architecture=poc_data["architecture"],
            implementation_steps=poc_data["steps"],
            code_snippet=poc_data["code"],
            metta_reasoning=poc_data["reasoning"],
            threat_addressed=poc_data["threat"],
            integration_notes="Integrates with existing Event Analyzer and Risk Assessor agents"
        )
        
        # Send result back to Master Orchestrator
        await ctx.send(sender, result)
        ctx.logger.info(f"✅ POC generated successfully: {result.poc_title}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error generating POC: {e}")
        # Send error response
        error_result = POCResult(
            request_id=msg.request_id,
            poc_title="POC Generation Failed",
            architecture="Error in processing",
            implementation_steps=["Error occurred during generation"],
            code_snippet="# Error: Could not generate POC",
            metta_reasoning=f"Error: {str(e)}",
            threat_addressed="N/A",
            integration_notes="Error occurred - integration not available"
        )
        await ctx.send(sender, error_result)

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle chat messages for testing via Agentverse"""
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            user_query = item.text.strip()
            ctx.logger.info(f"Got a POC generation query from {sender}: {user_query}")
            
            try:
                # Parse simple chat queries into POC requests
                if "defi" in user_query.lower():
                    domain = "defi"
                elif "nft" in user_query.lower():
                    domain = "nft"
                elif "security" in user_query.lower():
                    domain = "security"
                else:
                    domain = "blockchain"
                
                # Generate POC using MeTTa knowledge graph
                poc_data = process_poc_query(
                    requirements=user_query,
                    domain=domain,
                    risk_factors=[],
                    rag=poc_rag,
                    llm=llm
                )
                
                # Format response for chat
                answer_text = f"""🎯 **{poc_data['title']}**

🏗️ **Architecture:**
{poc_data['architecture']}

📋 **Implementation Steps:**
{chr(10).join([f"  {step}" for step in poc_data['steps'][:3]])}

⚡ **Threat Addressed:**
{poc_data['threat']}

🧠 **MeTTa Reasoning:**
{poc_data['reasoning'][:200]}...

💻 **Sample Code:**
```python
{poc_data['code'][:300]}...
```

This POC leverages your existing Event Analyzer and Risk Assessor agents!"""
                
                await ctx.send(sender, create_text_chat(answer_text))
                
            except Exception as e:
                ctx.logger.error(f"Error processing POC query: {e}")
                await ctx.send(
                    sender, 
                    create_text_chat("I apologize, but I encountered an error processing your POC request. Please provide requirements like 'Generate POC for DeFi risk monitoring'")
                )
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()