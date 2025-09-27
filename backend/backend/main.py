from flask import Flask, jsonify
import requests
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# The Graph API configuration
SUBGRAPH_URL = os.getenv('SUBGRAPH_URL', 'https://api.studio.thegraph.com/query/121751/eth-new-delhi/version/latest')
API_KEY = os.getenv('API_KEY', '')  # Default fallback

@app.route('/query/<contract_address>', methods=['GET'])
def query_subgraph(contract_address):
    try:
        # GraphQL query with contract address filter
        query = {
            "query": f"""
            {{
                verifiedPoCs(first: 10, where: {{target: "{contract_address}"}}) {{
                    id
                    pocHash
                    pocType
                    target
                    blockTimestamp
                    metadataURI
                    severity
                    summary
                }}
            }}
            """,
            "operationName": "Subgraphs",
            "variables": {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # Make request to The Graph
        response = requests.post(SUBGRAPH_URL, json=query, headers=headers)
        
        returnResponse = {}
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from subgraph"}), response.status_code
        if not (response.json().get('data') and response.json().get('data').get("verifiedPoCs")):
            print("No verifiedPoCs found") 
            print(f"contract Address:{contract_address} response.json(): {response.json()}")
            return jsonify(returnResponse)

        for item in response.json().get('data').get("verifiedPoCs"):
            print(item)
            if item.get('target') != contract_address:
                continue
            for key, value in item.items():
                print(f"{key}: {value}")
                returnResponse[key] = value
            if item.get('blockTimestamp'):
                timestamp = int(item.get('blockTimestamp'))
                dt_object = datetime.datetime.fromtimestamp(timestamp)
                returnResponse['blockTimestamp'] = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            else:
                returnResponse['blockTimestamp'] = "N/A"
        if response.status_code == 200:
            return jsonify(returnResponse)
        else:
            return jsonify({"error": "Failed to fetch data from subgraph"}), response.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Get port from environment (Railway, Render, Heroku use $PORT)
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)