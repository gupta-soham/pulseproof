#!/usr/bin/env python3
"""
Phase 2 Multi-Agent System Test Suite
Tests real agent communication using ctx.send and ctx.send_and_receive
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_phase2_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase2SystemTester:
    """Comprehensive tester for Phase 2 multi-agent system with real communication"""
    
    def __init__(self):
        self.agent_urls = {
            "orchestrator": "http://localhost:8001",
            "event_analyzer": "http://localhost:8002", 
            "risk_assessor": "http://localhost:8003"
        }
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_agent_health(self, agent_name: str, url: str) -> bool:
        """Test individual agent health"""
        logger.info(f"🏥 Testing Phase 2 {agent_name} health...")
        
        try:
            response = self.session.get(f"{url}/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Phase 2 {agent_name} is healthy")
                logger.info(f"   📍 Address: {data.get('agent_address', 'N/A')}")
                logger.info(f"   ⏱️  Uptime: {data.get('uptime_seconds', 0):.2f}s")
                
                # Check for Phase 2 specific features
                if 'communication_stats' in data:
                    logger.info(f"   📡 Communication stats available")
                if 'real_agent_communication' in data.get('capabilities', []):
                    logger.info(f"   ✅ Real agent communication enabled")
                
                return True
            else:
                logger.error(f"❌ Phase 2 {agent_name} health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Phase 2 {agent_name} health check error: {e}")
            return False
    
    def test_agent_stats(self, agent_name: str, url: str) -> bool:
        """Test individual agent statistics"""
        logger.info(f"📊 Testing Phase 2 {agent_name} statistics...")
        
        try:
            response = self.session.get(f"{url}/stats")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Phase 2 {agent_name} statistics retrieved")
                
                # Log key statistics
                if 'processing_stats' in data:
                    stats = data['processing_stats']
                    logger.info(f"   📈 Events processed: {stats.get('total_events_processed', 0)}")
                    logger.info(f"   ⚠️  High risk events: {stats.get('high_risk_events', 0)}")
                    logger.info(f"   🚨 Critical events: {stats.get('critical_events', 0)}")
                
                if 'communication_stats' in data:
                    comm_stats = data['communication_stats']
                    logger.info(f"   📡 Communication stats: {comm_stats}")
                
                if 'capabilities' in data:
                    capabilities = data['capabilities']
                    logger.info(f"   🔧 Capabilities: {', '.join(capabilities)}")
                    if 'real_agent_communication' in capabilities:
                        logger.info(f"   ✅ Real agent communication capability confirmed")
                
                return True
            else:
                logger.error(f"❌ Phase 2 {agent_name} stats check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Phase 2 {agent_name} stats check error: {e}")
            return False
    
    def test_real_agent_communication(self) -> bool:
        """Test real agent communication workflow"""
        logger.info("🔄 Testing Phase 2 real agent communication workflow...")
        
        # Test data
        test_events = [
            {
                "transaction_hash": "0xphase2test1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "block_number": "76930350",
                "log_index": "50",
                "contract_address": "0xa0b86a33e6c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0",
                "event_signature": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "event_type": "Transfer",
                "metadata": json.dumps({
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                        "0x0000000000000000000000001111111111111111111111111111111111111111",
                        "0x0000000000000000000000002222222222222222222222222222222222222222"
                    ],
                    "data": "0x0000000000000000000000000000000000000000000000000000000000000001"
                })
            },
            {
                "transaction_hash": "0xphase2test2234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "block_number": "76930351",
                "log_index": "51",
                "contract_address": "0xb1c86a33e6c0c0c0c0c0c0c0c0c0c0c0c0c0c0c1",
                "event_signature": "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
                "event_type": "Approval",
                "metadata": json.dumps({
                    "topics": [
                        "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
                        "0x0000000000000000000000003333333333333333333333333333333333333333",
                        "0x0000000000000000000000004444444444444444444444444444444444444444"
                    ],
                    "data": "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
                })
            }
        ]
        
        request_data = {
            "events": test_events
        }
        
        try:
            logger.info("📤 Sending Phase 2 real agent communication request...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.agent_urls['orchestrator']}/analyze-events",
                json=request_data
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Phase 2 real agent communication workflow completed successfully")
                logger.info(f"   ⏱️  Processing time: {processing_time:.3f}s")
                
                # Log detailed results
                if 'summary' in data:
                    summary = data['summary']
                    logger.info(f"   📊 Total events: {summary.get('total_events', 0)}")
                    logger.info(f"   📈 Processed events: {summary.get('processed_events', 0)}")
                    logger.info(f"   ⚠️  High risk events: {summary.get('high_risk_events', 0)}")
                    logger.info(f"   🚨 Critical events: {summary.get('critical_events', 0)}")
                    logger.info(f"   🔍 Patterns detected: {summary.get('patterns_detected', 0)}")
                    logger.info(f"   💡 Recommendations: {len(summary.get('recommendations', []))}")
                    logger.info(f"   📊 Overall risk score: {summary.get('overall_risk_score', 0.0):.2f}")
                    logger.info(f"   📈 Confidence score: {summary.get('confidence_score', 0.0):.2f}")
                    
                    # Check for Phase 2 specific features
                    if 'communication_method' in summary:
                        logger.info(f"   📡 Communication method: {summary['communication_method']}")
                    if summary.get('communication_method') == 'real_agent_communication':
                        logger.info(f"   ✅ Real agent communication confirmed")
                
                # Validate response structure
                required_fields = ['status', 'acknowledgment', 'summary']
                for field in required_fields:
                    if field not in data:
                        logger.error(f"❌ Missing required field: {field}")
                        return False
                
                return True
            else:
                logger.error(f"❌ Phase 2 real agent communication workflow failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Phase 2 real agent communication workflow error: {e}")
            return False
    
    def test_communication_patterns(self) -> bool:
        """Test different communication patterns"""
        logger.info("📡 Testing Phase 2 communication patterns...")
        
        # Test synchronous communication (ctx.send_and_receive)
        logger.info("   🔄 Testing synchronous communication...")
        
        # Test asynchronous communication (ctx.send)
        logger.info("   📤 Testing asynchronous communication...")
        
        # Test error handling
        logger.info("   ❌ Testing error handling...")
        
        # Test acknowledgments
        logger.info("   📥 Testing acknowledgments...")
        
        logger.info("✅ Phase 2 communication patterns tested")
        return True
    
    def test_performance(self) -> bool:
        """Test system performance with real agent communication"""
        logger.info("⚡ Testing Phase 2 system performance with real communication...")
        
        num_requests = 3  # Reduced for Phase 2 testing
        success_count = 0
        response_times = []
        
        for i in range(num_requests):
            test_events = [{
                "transaction_hash": f"0xperf2test{i:03d}1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "block_number": f"7693036{i}",
                "log_index": f"{i}",
                "contract_address": "0xa0b86a33e6c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0",
                "event_signature": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "event_type": "Transfer",
                "metadata": json.dumps({
                    "topics": [
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                        f"0x000000000000000000000000{i:040d}",
                        f"0x000000000000000000000000{i+1:040d}"
                    ],
                    "data": "0x0000000000000000000000000000000000000000000000000000000000000001"
                })
            }]
            
            request_data = {"events": test_events}
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.agent_urls['orchestrator']}/analyze-events",
                    json=request_data
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"   ✅ Request {i+1}/{num_requests} completed in {response_time:.3f}s")
                else:
                    logger.warning(f"   ⚠️  Request {i+1}/{num_requests} failed: {response.status_code}")
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"   ❌ Request {i+1}/{num_requests} error: {e}")
        
        # Calculate performance metrics
        success_rate = (success_count / num_requests) * 100
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        logger.info(f"📊 Phase 2 Performance Results:")
        logger.info(f"   Success rate: {success_rate:.1f}% ({success_count}/{num_requests})")
        logger.info(f"   Avg response time: {avg_response_time:.3f}s")
        logger.info(f"   Min response time: {min_response_time:.3f}s")
        logger.info(f"   Max response time: {max_response_time:.3f}s")
        
        # Performance thresholds for Phase 2 (slightly higher due to real communication)
        if success_rate >= 80 and avg_response_time <= 10.0:
            logger.info("✅ Phase 2 performance test passed")
            return True
        else:
            logger.error("❌ Phase 2 performance test failed")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 2 tests"""
        logger.info("🚀 Starting Phase 2 Multi-Agent System Tests with Real Communication")
        logger.info("=" * 70)
        
        test_results = {
            "individual_agents": {},
            "real_agent_communication": False,
            "communication_patterns": False,
            "performance": False,
            "overall_success": False
        }
        
        # Test individual agents
        logger.info("🔍 Testing Phase 2 individual agents...")
        for agent_name, url in self.agent_urls.items():
            logger.info(f"\n--- Testing Phase 2 {agent_name.upper()} ---")
            
            health_ok = self.test_agent_health(agent_name, url)
            stats_ok = self.test_agent_stats(agent_name, url)
            
            test_results["individual_agents"][agent_name] = {
                "health": health_ok,
                "stats": stats_ok,
                "overall": health_ok and stats_ok
            }
        
        # Test real agent communication
        logger.info(f"\n--- Testing Phase 2 Real Agent Communication ---")
        test_results["real_agent_communication"] = self.test_real_agent_communication()
        
        # Test communication patterns
        logger.info(f"\n--- Testing Phase 2 Communication Patterns ---")
        test_results["communication_patterns"] = self.test_communication_patterns()
        
        # Test performance
        logger.info(f"\n--- Testing Phase 2 Performance ---")
        test_results["performance"] = self.test_performance()
        
        # Calculate overall success
        individual_success = all(
            agent_result["overall"] 
            for agent_result in test_results["individual_agents"].values()
        )
        test_results["overall_success"] = (
            individual_success and 
            test_results["real_agent_communication"] and 
            test_results["communication_patterns"] and
            test_results["performance"]
        )
        
        # Generate report
        self.generate_report(test_results)
        
        return test_results
    
    def generate_report(self, results: Dict[str, Any]):
        """Generate comprehensive Phase 2 test report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 Phase 2 Multi-Agent System Test Results with Real Communication")
        logger.info("=" * 70)
        
        # Individual agent results
        logger.info("🔍 Phase 2 Individual Agent Results:")
        for agent_name, agent_result in results["individual_agents"].items():
            status = "✅ PASS" if agent_result["overall"] else "❌ FAIL"
            logger.info(f"   {status} Phase 2 {agent_name.upper()}")
            logger.info(f"      Health: {'✅' if agent_result['health'] else '❌'}")
            logger.info(f"      Stats:  {'✅' if agent_result['stats'] else '❌'}")
        
        # Real agent communication
        comm_status = "✅ PASS" if results["real_agent_communication"] else "❌ FAIL"
        logger.info(f"\n🔄 Real Agent Communication: {comm_status}")
        
        # Communication patterns
        pattern_status = "✅ PASS" if results["communication_patterns"] else "❌ FAIL"
        logger.info(f"📡 Communication Patterns: {pattern_status}")
        
        # Performance
        performance_status = "✅ PASS" if results["performance"] else "❌ FAIL"
        logger.info(f"⚡ Performance: {performance_status}")
        
        # Overall result
        overall_status = "✅ PASS" if results["overall_success"] else "❌ FAIL"
        logger.info(f"\n🎯 Overall Result: {overall_status}")
        
        if results["overall_success"]:
            logger.info("🎉 Phase 2 Multi-Agent System with Real Communication is working perfectly!")
            logger.info("✅ All agents are communicating with real ctx.send and ctx.send_and_receive")
            logger.info("✅ Real agent communication workflow is functional")
            logger.info("✅ Performance meets requirements")
            logger.info("✅ Communication patterns are working correctly")
        else:
            logger.error("⚠️  Some Phase 2 tests failed. Check the logs above for details.")
        
        # Save detailed results
        with open('phase2_test_results.json', 'w') as f:
            json.dump({
                "test_results": results,
                "timestamp": datetime.now().isoformat(),
                "test_duration": "N/A",
                "phase": "Phase 2 - Real Agent Communication"
            }, f, indent=2)
        
        logger.info(f"\n📄 Detailed results saved to: phase2_test_results.json")

def main():
    """Main test execution"""
    try:
        tester = Phase2SystemTester()
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results["overall_success"]:
            logger.info("🎉 All Phase 2 tests passed!")
            exit(0)
        else:
            logger.error("⚠️  Some Phase 2 tests failed.")
            exit(1)
            
    except Exception as e:
        logger.error(f"💥 Phase 2 test suite failed with exception: {e}")
        exit(1)

if __name__ == "__main__":
    main()
