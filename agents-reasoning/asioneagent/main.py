import os, json, requests, traceback
from pathlib import Path
from typing import Dict, Any

# Set your ASI:One API key
ASI_KEY = os.getenv("ASI_KEY")

ASI_URL = "https://api.asi1.ai/v1/chat/completions"

from dotenv import load_dotenv
# Look for .env file in the eth-global directory (parent of agents)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"No .env file found at: {env_path}")
    load_dotenv()

def generate_poc_metadata(event: Dict[str, Any], poc_from_red_agent: str, risk_score: float) -> Dict[str, Any]:
    """
    Calls ASI:One to reason about the event and produce structured PoC metadata.
    """
    prompt = f"""
You are a responsible blockchain security analyst. DO NOT produce runnable exploit code or step-by-step exploit payloads.
Given the event JSON and a PoC template (which may be inaccurate), return ONLY valid JSON with the following keys:
- issueName: short descriptive title
- pocSummary: one-line summary of vulnerability(no exploit code)
- pocType: type of vulnerability (e.g. REENTRANCY, OVERFLOW, ACCESS_CONTROL, etc.) 
- poc: a **Solidity code snippet** demonstrating the vulnerability and how to exploit it (as a Foundry test)
- severity: one of "low","medium","high","critical" based on risk_score
- summary: one-sentence overall explanation including confidence percentage (risk_score*100%)

Respond ONLY with valid JSON, no markdown, no extra text.
Event:
{json.dumps(event, separators=(',',':'))}

PoC Template: {poc_from_red_agent}
Risk Score: {risk_score}
"""

    headers = {
        "Authorization": f"Bearer {ASI_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    r = requests.post(ASI_URL, headers=headers, json=body, timeout=20)
    r.raise_for_status()

    content = r.json()["choices"][0]["message"]["content"].strip()
    return json.loads(content)


if __name__ == "__main__":
    sample_event = {
        "transaction_hash": "0xabc123",
        "block_number": 17000000,
        "contract_address": "0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF",
        "event_signature": "Transfer(address,address,uint256)",
        "event_type": "Transfer",
        "metadata": {"topics": [], "data": ""}
    }

    result = generate_poc_metadata(sample_event, vulnerability="REENTRANCY", risk_score=0.85)
    print(json.dumps(result, indent=2))
