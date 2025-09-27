#!/usr/bin/env python3
"""
realistic_events.py

Real suspicious events from Ethereum mainnet that would trigger security concerns.
Based on actual exploit patterns and suspicious activities.
"""
import os
import sys
import requests
import json
import time
from typing import List, Dict, Any

# Ensure project root is on sys.path for direct imports when running from this folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agents-reasoning.poc_sender_agent.main import register_poc  # type: ignore
from agents-reasoning.asioneagent.main import generate_poc_metadata  # type: ignore
# Optional integrations flags
# ENABLE_ASI = os.getenv("ENABLE_ASI_METADATA", "true").lower() == "true"
ENABLE_ASI = True
MIN_RISK_FOR_CHAIN = float(os.getenv("MIN_RISK_FOR_CHAIN", "0.35"))


def get_realistic_suspicious_events() -> List[Dict]:
    """
    Returns realistic suspicious events based on actual mainnet patterns:
    1. Flash loan attack pattern (large borrows/repays)
    2. Reentrancy pattern (multiple transfers in single tx)  
    3. Unlimited approval to suspicious contract
    4. Massive token drain (large transfers to EOA)
    5. Sandwich attack pattern (MEV exploit)
    """
    
    return [
        {
            # Flash loan attack pattern - Compound/Aave large borrow
            "transaction_hash": "0x1234567890abcdef1111111111111111111111111111111111111111111111111111",
            "block_number": 18500000,
            "log_index": 1,
            "event_type": "Transfer",
            "event_name": "Transfer",  # Legacy field
            "event_signature": "Transfer(address,address,uint256)",
            "contract_address": "0xA0b86a33E6411B1C8479D3a37B0A8b7Dc5DD3B14",  # cDAI
            "metadata": {
                "args": {
                    "from": "0x0000000000000000000000000000000000000000",  # Mint
                    "to": "0x1234567890123456789012345678901234567890",    # Attacker
                    "value": "50000000000000000000000000"  # 50M DAI worth
                }
            }
        },
        {
            # Reentrancy attack - Suspicious multiple transfers
            "transaction_hash": "0x2345678901bcdef2222222222222222222222222222222222222222222222222",
            "block_number": 18500001,
            "log_index": 2,
            "event_type": "Transfer",
            "event_name": "Transfer",  # Legacy field
            "event_signature": "Transfer(address,address,uint256)",
            "contract_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "metadata": {
                "args": {
                    "from": "0x1111111111111111111111111111111111111111",    # DeFi Protocol
                    "to": "0x2345678901234567890123456789012345678901",      # Attacker
                    "value": "1000000000000000000000"  # 1000 ETH
                }
            }
        },
        {
            # Unlimited approval to suspicious contract
            "transaction_hash": "0x3456789012cdef33333333333333333333333333333333333333333333333333",
            "block_number": 18500002,
            "log_index": 3,
            "event_type": "Approval",
            "event_name": "Approval",  # Legacy field
            "event_signature": "Approval(address,address,uint256)",
            "contract_address": "0xA0b86a33E6411B1C8479D3a37B0A8b7Dc5DD3B14",  # USDC
            "metadata": {
                "args": {
                    "owner": "0x3333333333333333333333333333333333333333",     # Victim
                    "spender": "0x4444444444444444444444444444444444444444",   # Malicious contract
                    "value": "115792089237316195423570985008687907853269984665640564039457584007913129639935"  # Max uint256
                }
            }
        },
        {
            # Token drain - Large transfer to EOA 
            "transaction_hash": "0x4567890123def444444444444444444444444444444444444444444444444444444",
            "block_number": 18500003,
            "log_index": 4,
            "event_type": "Transfer",
            "event_name": "Transfer",  # Legacy field
            "event_signature": "Transfer(address,address,uint256)",
            "contract_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            "metadata": {
                "args": {
                    "from": "0x5555555555555555555555555555555555555555",    # DeFi Protocol treasury  
                    "to": "0x6666666666666666666666666666666666666666",      # Attacker EOA
                    "value": "10000000000000000000000000"  # 10M DAI
                }
            }
        },
        {
            # MEV Sandwich attack - Front-run large swap
            "transaction_hash": "0x5678901234ef55555555555555555555555555555555555555555555555555555",
            "block_number": 18500004,
            "log_index": 5,
            "event_type": "Swap",
            "event_name": "Swap",  # Legacy field
            "event_signature": "Swap(address,uint256,uint256,uint256,uint256,address)",
            "contract_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2 Router
            "metadata": {
                "args": {
                    "sender": "0x7777777777777777777777777777777777777777",     # MEV bot
                    "to": "0x8888888888888888888888888888888888888888",        # MEV bot
                    "amount0In": "5000000000000000000000",   # 5000 ETH
                    "amount1In": "0",
                    "amount0Out": "0", 
                    "amount1Out": "15000000000000000000000000"  # 15M USDC
                }
            }
        },
        {
            # Governance attack - Large token transfer before proposal
            "transaction_hash": "0x6789012345f66666666666666666666666666666666666666666666666666666666",
            "block_number": 18500005,
            "log_index": 6,
            "event_type": "Transfer",
            "event_name": "Transfer",  # Legacy field
            "event_signature": "Transfer(address,address,uint256)",
            "contract_address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # UNI token
            "metadata": {
                "args": {
                    "from": "0x9999999999999999999999999999999999999999",    # Whale accumulator
                    "to": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",      # Governance attacker
                    "value": "10000000000000000000000000"  # 10M UNI tokens
                }
            }
        },
        {
            # Bridge exploit - Large mint/burn pattern
            "transaction_hash": "0x789012345f777777777777777777777777777777777777777777777777777777",
            "block_number": 18500006,
            "log_index": 7,
            "event_type": "Transfer",
            "event_name": "Transfer",  # Legacy field
            "event_signature": "Transfer(address,address,uint256)",
            "contract_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # WBTC
            "metadata": {
                "args": {
                    "from": "0x0000000000000000000000000000000000000000",    # Mint (suspicious)
                    "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",      # Attacker
                    "value": "100000000000"  # 1000 BTC worth
                }
            }
        }
    ]


def enrich_and_register(event: Dict[str, Any], analysis: Dict[str, Any]):
    risk_score = analysis.get("risk_score", 0.0)
    poc_from_red_agent = analysis['poc']
    if not ENABLE_ASI:
        print("  [ASI] Skipped (ENABLE_ASI_METADATA=false)")
        return
    if risk_score < MIN_RISK_FOR_CHAIN:
        print(f"  [ASI] Skipped (risk {risk_score:.2f} < threshold {MIN_RISK_FOR_CHAIN})")
        return
    if generate_poc_metadata is None:
        print("  [ASI] generate_poc_metadata not available")
        return
    if register_poc is None:
        print("  [CHAIN] register_poc not available")
        return
    try:
        print("  [ASI] Generating PoC metadata via ASI:One...")
        meta = generate_poc_metadata({
            "transaction_hash": event.get("transaction_hash"),
            "block_number": event.get("block_number"),
            "contract_address": event.get("contract_address"),
            "event_type": event.get("event_type"),
            "event_signature": event.get("event_signature"),
            "metadata": event.get("metadata", {})
        }, poc_from_red_agent=poc_from_red_agent, risk_score=risk_score)
        # Normalize severity (ASI may return text)
        sev = str(meta.get("severity", "low")).lower()
        poc_code = meta.get("poc") or meta.get("pocCode") or "// No PoC code returned"
        poc_id = meta.get("issueName", f"auto_{int(time.time())}").replace(" ", "_")
        poc_type = meta.get("pocType", "unknown").lower()
        filename = f"{poc_id}.t.sol"
        print("  [ASI] Metadata received; registering on-chain...")
        chain_resp = register_poc(
            poc_source=poc_code.encode(),
            poc_filename=filename,
            poc_id=poc_id,
            poc_type=poc_type,
            target=event.get("contract_address", "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"),
            block_number=event.get("block_number", 0),
            severity=sev,
            summary=meta.get("pocSummary") or meta.get("summary", "Generated by ASI")
        )
        print(f"  [CHAIN] Registered PoC tx: {chain_resp.get('tx_hash','<no tx hash>')}")
    except Exception as e:
        print(f"  [ERROR] ASI/registration failed: {e}")


def test_with_realistic_events():
    """Test the pipeline with realistic suspicious events"""
    print("Testing Eth-Global Security Pipeline with REALISTIC suspicious events...")
    print("=" * 80)
    
    events = get_realistic_suspicious_events()
    
    # Health check first
    try:
        health_response = requests.get("http://localhost:8001/health", timeout=10)
        if health_response.status_code == 200:
            print(f"Health check: {health_response.json()}")
        else:
            print(f"Health check failed: {health_response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Health check error: {e}")
        print("Make sure the red_agent server is running on localhost:8001")
        return

    # Test analysis with realistic events
    print(f"\nAnalyzing {len(events)} REALISTIC suspicious events...")
    print("Processing with appropriate delays between events...")
    
    request_data = {
        "events": events
    }

    try:
        # Add processing delay to simulate real-time analysis
        print("Sending events for analysis (simulating real-time processing)...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8001/analyze-events", 
            json=request_data,
            timeout=60  # Longer timeout for complex analysis
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code != 200:
            print(f"Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return

        result = response.json()
        print(f"Analysis completed in {processing_time:.2f} seconds")

        # Display results with enhanced formatting
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"Total events: {result['total_events']}")
        print(f"Analyzed: {result['analyzed']}")
        print(f"PoCs generated: {result['pocs_generated']}")
        print("=" * 80)

        high_risk_count = 0
        medium_risk_count = 0

        for i, analysis in enumerate(result['results']):
            risk_score = analysis['risk_score']
            confidence = analysis.get('confidence', 0)
            
            # Risk categorization
            if risk_score >= 0.7:
                risk_level = "HIGH RISK"
                high_risk_count += 1
            elif risk_score >= 0.4:
                risk_level = " MEDIUM RISK" 
                medium_risk_count += 1
            else:
                risk_level = "📊 LOW RISK"
                
            print(f"\n{risk_level} - Event {i+1}: {analysis['event_id'][:20]}...")
            print(f"  Risk Score: {risk_score:.4f}")
            print(f"  Confidence: {confidence:.4f}")
            print(f"  Vulnerability: {analysis['vulnerability']}")
            print(f"  PoC Generated: {' YES' if analysis['poc_generated'] else '❌ NO'}")
            
            if analysis['poc_generated']:
                poc = analysis['poc']
                print(f"  PoC ID: {poc['poc_id']}")
                print(f"  Status: {poc['status']}")
                print(f"  Description: {poc['description'][:100]}...")
                print(f"  Severity: {poc['severity']}")
                print(f"  Est. Impact: ${poc['estimated_impact']:,.2f}")
                print(f"  Code Length: {len(poc['foundry_test_code']):,} chars")
                
                if poc.get('out_path'):
                    print(f"     Saved to: {poc['out_path']}")
                enrich_and_register(events[i], analysis)


            if analysis.get('error'):
                print(f"     ERROR: {analysis['error']}")
                
            # Add small delay between displaying results for readability
            time.sleep(0.5)

        # Summary statistics
        print(f"\nSECURITY SUMMARY")
        print(f"High Risk Events: {high_risk_count}")
        print(f"Medium Risk Events: {medium_risk_count}")
        print(f"Low Risk Events: {len(events) - high_risk_count - medium_risk_count}")
        print(f"Total PoCs Generated: {result['pocs_generated']}")
        print(f"Total Processing Time: {processing_time:.2f}s")
        print(f"Events/Second: {len(events)/processing_time:.2f}")

    except requests.exceptions.Timeout:
        print(" Request timed out - analysis is taking longer than expected")
        print("   This might indicate complex PoC generation in progress...")
    except requests.exceptions.RequestException as e:
        print(f" Error calling API: {e}")
        print("   Make sure the red_agent service is running on localhost:8001")
    except Exception as e:
        print(f" Unexpected error: {e}")


if __name__ == "__main__":
    test_with_realistic_events()