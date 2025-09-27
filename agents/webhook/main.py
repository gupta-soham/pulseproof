import json
import logging
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubstreamsWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests from Substreams webhook sink"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read the request body
            post_data = self.rfile.read(content_length)
            
            # Parse JSON payload
            payload = json.loads(post_data.decode('utf-8'))
            
            # Process the webhook data
            self.process_webhook_data(payload)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"status": "success", "message": "Webhook processed"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def process_webhook_data(self, payload):
        """Process the webhook data from Substreams"""
        logger.info("=== Substreams Webhook Data ===")
        
        # Extract clock information
        if 'clock' in payload:
            clock = payload['clock']
            logger.info(f"Block Number: {clock.get('number', 'N/A')}")
            logger.info(f"Block ID: {clock.get('id', 'N/A')}")
            logger.info(f"Timestamp: {clock.get('timestamp', 'N/A')}")
        
        # Extract manifest information
        if 'manifest' in payload:
            manifest = payload['manifest']
            logger.info(f"Module Name: {manifest.get('moduleName', 'N/A')}")
            logger.info(f"Output Type: {manifest.get('type', 'N/A')}")
        
        # Process the actual data from your Substreams module
        if 'data' in payload:
            data = payload['data']
            logger.info(f"Data: {json.dumps(data, indent=2)}")
            
            # Here you can process your CandidateEvents data
            if 'events' in data:
                events = data['events']
                logger.info(f"Received {len(events)} candidate events")
                
                for i, event in enumerate(events):
                    logger.info(f"Event {i+1}:")
                    logger.info(f"  Transaction Hash: {event.get('transactionHash', 'N/A')}")
                    logger.info(f"  Block Number: {event.get('blockNumber', 'N/A')}")
                    logger.info(f"  Contract Address: {event.get('contractAddress', 'N/A')}")
                    logger.info(f"  Event Type: {event.get('eventType', 'N/A')}")
                    logger.info(f"  Event Signature: {event.get('eventSignature', 'N/A')}")
                
                # Call the phase2_orchestrator analyze-events handler
                self.call_phase2_orchestrator(events)
        
        logger.info("=== End Webhook Data ===")

    def call_phase2_orchestrator(self, events):
        """Call the analyze-events handler in phase2_orchestrator.py"""
        try:
            # Prepare the payload for the phase2 orchestrator
            orchestrator_payload = {
                "events": events
            }
            
            # Make HTTP request to phase2_orchestrator
            orchestrator_url = "http://localhost:8001/analyze-events"  # Adjust port as needed
            
            logger.info(f"Calling phase2_orchestrator at {orchestrator_url}")
            
            response = requests.post(
                orchestrator_url,
                json=orchestrator_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Successfully called phase2_orchestrator analyze-events")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(f"Phase2 orchestrator returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling phase2_orchestrator: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling phase2_orchestrator: {e}")

    def log_message(self, format, *args):
        """Override to use our logger instead of stderr"""
        logger.info(f"HTTP Request: {format % args}")

def serve():
    """Start the HTTP webhook server"""
    server_address = ('', 50051)
    httpd = HTTPServer(server_address, SubstreamsWebhookHandler)
    
    logger.info("Substreams HTTP Webhook server listening on port 50051")
    logger.info("Ready to receive webhook calls from: substreams sink webhook http://localhost:50051 ...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopping...")
        httpd.server_close()

if __name__ == "__main__":
    serve()
