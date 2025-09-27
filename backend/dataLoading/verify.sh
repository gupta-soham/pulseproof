#!/bin/bash

# Contract Verification Script for Etherscan
# Usage: ./verify.sh <network> <contract_address> <contract_name>

set -e

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <network> <contract_address> <contract_name>"
    echo "Example: $0 sepolia 0x8e048A20AC9743CA1132873A0c67b660d80D870a PoCRegistry"
    exit 1
fi

NETWORK=$1
CONTRACT_ADDRESS=$2
CONTRACT_NAME=$3

# API Key from hardhat.config.js
ETHERSCAN_API_KEY="GYIKIY1SSN7AWMSKUFE1AYG6NWCRW35WYM"

# Network URLs
case $NETWORK in
    "mainnet")
        API_URL="https://api.etherscan.io/api"
        EXPLORER_URL="https://etherscan.io"
        ;;
    "sepolia")
        API_URL="https://api-sepolia.etherscan.io/api"
        EXPLORER_URL="https://sepolia.etherscan.io"
        ;;
    "polygon")
        API_URL="https://api.polygonscan.com/api"
        EXPLORER_URL="https://polygonscan.com"
        ;;
    *)
        echo "Unsupported network: $NETWORK"
        exit 1
        ;;
esac

echo "🔍 Verifying contract $CONTRACT_NAME at $CONTRACT_ADDRESS on $NETWORK..."

# Get contract source code
if [ ! -f "contracts/$CONTRACT_NAME.sol" ]; then
    echo "❌ Contract file not found: contracts/$CONTRACT_NAME.sol"
    exit 1
fi

SOURCE_CODE=$(cat contracts/$CONTRACT_NAME.sol)

# Flatten source code (basic - replace import with comment)
SOURCE_CODE_FLATTENED=$(echo "$SOURCE_CODE" | sed 's|import "@openzeppelin/contracts/access/Ownable.sol";|// OpenZeppelin Ownable contract (flattened for verification)|')

# Submit verification request
echo "📤 Submitting verification request..."

RESPONSE=$(curl -s -X POST "$API_URL" \
  -d "apikey=$ETHERSCAN_API_KEY" \
  -d "module=contract" \
  -d "action=verifysourcecode" \
  -d "contractaddress=$CONTRACT_ADDRESS" \
  -d "sourceCode=$SOURCE_CODE_FLATTENED" \
  -d "codeformat=solidity-single-file" \
  -d "contractname=$CONTRACT_NAME" \
  -d "compilerversion=v0.8.20+commit.a1b79de6" \
  -d "optimizationUsed=1" \
  -d "runs=200" \
  -d "constructorArguements=" \
  -d "evmversion=paris" \
  -d "licenseType=3")

echo "Response: $RESPONSE"

# Parse response
STATUS=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', '0'))")
MESSAGE=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('message', 'Unknown error'))")

if [ "$STATUS" = "1" ]; then
    GUID=$(echo $RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', ''))")
    echo "✅ Verification submitted successfully! GUID: $GUID"
    
    # Check verification status
    echo "⏳ Checking verification status..."
    
    for i in {1..10}; do
        sleep 5
        echo "Attempt $i/10..."
        
        STATUS_RESPONSE=$(curl -s "$API_URL?guid=$GUID&module=contract&action=checkverifystatus&apikey=$ETHERSCAN_API_KEY")
        VERIFICATION_STATUS=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', ''))")
        
        echo "Status: $VERIFICATION_STATUS"
        
        if [[ "$VERIFICATION_STATUS" == *"Pass - Verified"* ]]; then
            echo "🎉 Contract verified successfully!"
            echo "🔗 View on explorer: $EXPLORER_URL/address/$CONTRACT_ADDRESS"
            exit 0
        elif [[ "$VERIFICATION_STATUS" == *"Fail"* ]]; then
            echo "❌ Verification failed: $VERIFICATION_STATUS"
            exit 1
        fi
    done
    
    echo "⏰ Verification check timed out. Please check manually: $EXPLORER_URL/address/$CONTRACT_ADDRESS"
    
else
    echo "❌ Verification submission failed: $MESSAGE"
    exit 1
fi