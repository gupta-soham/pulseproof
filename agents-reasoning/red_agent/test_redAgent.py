import requests
import json
from pprint import pprint

# Test data with various event types
SAMPLE_EVENTS = {
    "events": [
        {
            "transaction_hash": "0xabc123456789def0000000000000000000000000000000000000000000000000",
            "block_number": 17000000,
            "log_index": 5,
            "contract_address": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "event_signature": "Transfer(address,address,uint256)",
            "event_type": "Transfer",
            "event_name": "Transfer",
            "metadata": {
                "args": {
                    "from": "0x1111111111111111111111111111111111111111",
                    "to": "0x2222222222222222222222222222222222222222",
                    "value": "100000000000000000000"  # 100 ETH - high risk
                }
            }
        },
        {
            "transaction_hash": "0xdef987654321abc0000000000000000000000000000000000000000000000000",
            "block_number": 17000001,
            "log_index": 2,
            "contract_address": "0xcafecafecafecafecafecafecafecafecafecafe",
            "event_signature": "Transfer(address,address,uint256)",
            "event_type": "Transfer",
            "event_name": "Transfer",
            "metadata": {
                "args": {
                    "from": "0x1111111111111111111111111111111111111111",
                    "to": "0x0000000000000000000000000000000000000000",  # Zero address
                    "value": "5000000000000000000"  # 5 ETH
                }
            }
        },
        {
            "transaction_hash": "0x123456789abcdef0000000000000000000000000000000000000000000000000",
            "block_number": 17000002,
            "log_index": 8,
            "contract_address": "0xbeefbeefbeefbeefbeefbeefbeefbeefbeefbeef",
            "event_signature": "Approval(address,address,uint256)",
            "event_type": "Approval",
            "event_name": "Approval",
            "metadata": {
                "args": {
                    "owner": "0x3333333333333333333333333333333333333333",
                    "spender": "0x4444444444444444444444444444444444444444",
                    "value": "1000000000000000000000000"  # 1,000,000 ETH - excessive approval
                }
            }
        },
        {
            "transaction_hash": "0x987654321cba000000000000000000000000000000000000000000000000000",
            "block_number": 17000003,
            "log_index": 1,
            "contract_address": "0x1234123412341234123412341234123412341234",
            "event_signature": "Transfer(address,address,uint256)",
            "event_type": "Transfer",
            "event_name": "Transfer",
            "metadata": {
                "args": {
                    "from": "0x0000000000000000000000000000000000000000",  # Zero address (minting)
                    "to": "0x5555555555555555555555555555555555555555",
                    "value": "1000000000000000000"  # 1 ETH - low risk
                }
            }
        },
        {
            "transaction_hash": "0xabcdef1234567890000000000000000000000000000000000000000000000000",
            "block_number": 17000004,
            "log_index": 3,
            "contract_address": "0x5678567856785678567856785678567856785678",
            "event_signature": "Transfer(address,address,uint256)",
            "event_type": "Transfer",
            "event_name": "Transfer",
            "metadata": {
                "args": {
                    "from": "0x6666666666666666666666666666666666666666",
                    "to": "0x7777777777777777777777777777777777777777",
                    "value": "100000000000000000"  # 0.1 ETH - low risk
                }
            }
        }
    ]
}

def test_analyze_events():
    """Test the analyze-events endpoint"""
    url = "http://localhost:8001/analyze-events"
    
    try:
        response = requests.post(url, json=SAMPLE_EVENTS)
        response.raise_for_status()
        
        result = response.json()
        
        print("=== ANALYSIS RESULTS ===")
        print(f"Total events: {result['total_events']}")
        print(f"Analyzed: {result['analyzed']}")
        print(f"PoCs generated: {result['pocs_generated']}")
        print("\n" + "="*50 + "\n")
        
        for i, analysis in enumerate(result['results']):
            print(f"Event {i+1}: {analysis['event_id']}")
            print(f"  Risk Score: {analysis['risk_score']:.4f}")
            print(f"  Confidence: {analysis.get('confidence', 'N/A'):.4f}" if analysis.get('confidence') else "  Confidence: N/A")
            print(f"  Vulnerability: {analysis['vulnerability']}")
            print(f"  PoC Generated: {analysis['poc_generated']}")
            
            if analysis['poc_generated']:
                poc = analysis['poc']
                print(f"  PoC ID: {poc['poc_id']}")
                print(f"  Status: {poc['status']}")
                print(f"  Description: {poc['description']}")
                print(f"  Severity: {poc['severity']}")
                print(f"  Estimated Impact: {poc['estimated_impact']}")
                print(f"  PoC Code Length: {len(poc['foundry_test_code'])} characters")
                if poc.get('out_path'):
                    print(f"  Saved to: {poc['out_path']}")
                else:
                    print(f"  File: Not saved to disk")
            else:
                print(f"  Reason: {analysis.get('reason', 'N/A')}")
            
            if analysis.get('error'):
                print(f"  ERROR: {analysis['error']}")
            
            print("-" * 30)
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
        print("Make sure the service is running on localhost:8001")

def test_health():
    """Test health endpoint"""
    url = "http://localhost:8001/health"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Health check:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    print("Testing Eth-Global Security Pipeline API...\n")
    
    # Test health endpoint first
    test_health()
    print("\n")
    
    # Test main analysis endpoint
    test_analyze_events()