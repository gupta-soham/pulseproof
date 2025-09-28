import json
from openai import OpenAI
from .investment_rag import POCRAG

class LLM:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.asi1.ai/v1"
        )

    def create_completion(self, prompt, max_tokens=200):
        completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="asi1-mini",
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content

def get_poc_intent_and_domain(query, llm):
    """Use ASI:One API to classify POC generation intent and extract domain/keywords."""
    prompt = (
        f"Given the POC generation query: '{query}'\n"
        "Classify the intent as one of: 'poc_generation', 'domain_specific', 'architecture_advice', 'implementation_steps', 'risk_based', 'threat_based', 'faq', or 'unknown'.\n"
        "Extract the domain (defi, nft, security, blockchain) and any relevant keywords (monitor, dashboard, risk, authenticity, etc.).\n"
        "Return *only* the result in JSON format like this, with no additional text:\n"
        "{\n"
        "  \"intent\": \"<classified_intent>\",\n"
        "  \"domain\": \"<extracted_domain>\",\n"
        "  \"keyword\": \"<extracted_keyword>\"\n"
        "}"
    )
    response = llm.create_completion(prompt, max_tokens=150)
    try:
        result = json.loads(response)
        return result["intent"], result.get("domain", "security"), result.get("keyword", "")
    except json.JSONDecodeError:
        print(f"Error parsing ASI:One response: {response}")
        return "unknown", "security", ""

def generate_poc_knowledge_response(query, intent, domain, keyword, llm):
    """Use ASI:One to generate a response for new POC knowledge based on intent."""
    if intent == "poc_generation":
        prompt = (
            f"Query: '{query}'\n"
            f"The domain '{domain}' has no specific POC for '{keyword}' in my knowledge base. Suggest a relevant POC type.\n"
            "Return *only* the POC type name, no additional text."
        )
    elif intent == "domain_specific":
        prompt = (
            f"Query: '{query}'\n"
            f"The domain '{domain}' needs new POC recommendations. Suggest appropriate blockchain security POCs.\n"
            "Return *only* the POC recommendations, no additional text."
        )
    elif intent == "architecture_advice":
        prompt = (
            f"Query: '{query}'\n"
            f"The POC '{keyword}' has no architecture pattern in my knowledge base. Suggest appropriate architecture.\n"
            "Return *only* the architecture pattern, no additional text."
        )
    elif intent == "implementation_steps":
        prompt = (
            f"Query: '{query}'\n"
            f"The POC '{keyword}' has no implementation steps in my knowledge base. Suggest step-by-step implementation.\n"
            "Return *only* the implementation steps, no additional text."
        )
    elif intent == "faq":
        prompt = (
            f"Query: '{query}'\n"
            "This is a new POC question not in my knowledge base. Provide a helpful, concise answer about blockchain security POCs.\n"
            "Return *only* the answer, no additional text."
        )
    else:
        return None
    return llm.create_completion(prompt, max_tokens=200)

def process_poc_query(requirements, domain, risk_factors, rag: POCRAG, llm: LLM):
    """Process POC generation request using MeTTa knowledge graph reasoning."""
    print(f"🧠 Processing POC query: Requirements={requirements}, Domain={domain}, Risk Factors={risk_factors}")
    
    # Find the best POC type for requirements and domain
    best_poc = rag.find_best_poc_for_requirements(requirements, domain)
    
    if not best_poc:
        # Fallback to domain POCs
        domain_pocs = rag.query_domain_pocs(domain)
        best_poc = domain_pocs[0] if domain_pocs else "risk_monitoring_dashboard"
    
    print(f"🎯 Selected POC type: {best_poc}")
    
    # Get POC details from MeTTa knowledge graph
    architecture = rag.get_poc_architecture(best_poc)
    implementation_steps = rag.get_poc_implementation_steps(best_poc)
    code_template = rag.get_poc_code_template(best_poc)
    complexity = rag.get_complexity_level(best_poc)
    development_time = rag.get_development_time(best_poc)
    
    # Extract step-by-step list from implementation steps
    if implementation_steps:
        steps_text = implementation_steps[0]
        # Split by numbers and clean up
        steps_list = [step.strip() for step in steps_text.split(',') if step.strip()]
    else:
        steps_list = [
            "1. Set up blockchain event monitoring",
            "2. Integrate with existing Event Analyzer agent",
            "3. Connect to Risk Assessor agent", 
            "4. Build alert and response system",
            "5. Deploy and test the POC"
        ]
    
    # Create threat context from risk factors
    threat_context = ""
    if risk_factors:
        threat_context = f"Addresses threats: {', '.join(risk_factors)}"
    else:
        threat_context = f"General {domain} security enhancement"
    
    # MeTTa reasoning explanation
    metta_reasoning = f"""MeTTa Knowledge Graph Reasoning:
📊 Domain Analysis: {domain} → Selected POC type: {best_poc}
🏗️ Architecture Pattern: {architecture[0] if architecture else 'Event-driven security architecture'}
⚡ Complexity: {complexity[0] if complexity else 'Medium complexity'}
⏱️ Timeline: {development_time[0] if development_time else '2-4 weeks'}
🎯 Integration: Leverages existing Event Analyzer and Risk Assessor agents
"""
    
    return {
        "title": f"POC: {best_poc.replace('_', ' ').title()}",
        "architecture": architecture[0] if architecture else "Event Listener → Event Analyzer → Risk Assessor → Alert System",
        "steps": steps_list,
        "code": code_template[0] if code_template else generate_fallback_code(best_poc, requirements),
        "reasoning": metta_reasoning,
        "threat": threat_context,
        "complexity": complexity[0] if complexity else "medium",
        "timeline": development_time[0] if development_time else "2-4 weeks"
    }

def generate_fallback_code(poc_type, requirements):
    """Generate fallback code template if not found in knowledge graph."""
    return f'''
# POC: {poc_type.replace('_', ' ').title()}
# Requirements: {requirements}

async def {poc_type}_main():
    """Main POC function for {poc_type}"""
    while True:
        # Monitor blockchain events
        event = await blockchain_listener.get_next_event()
        
        # Use existing Event Analyzer agent
        analysis = await event_analyzer_agent.analyze(event)
        
        # Use existing Risk Assessor agent
        risk = await risk_assessor_agent.assess(analysis)
        
        # Take action based on risk level
        if risk.risk_level == "HIGH":
            await alert_system.notify(f"🚨 High risk detected: {{risk.recommendation}}")
            
        await asyncio.sleep(1)  # Processing interval

if __name__ == "__main__":
    asyncio.run({poc_type}_main())
'''