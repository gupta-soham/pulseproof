#!/bin/bash

# Contract Verification Script for Etherscan
# Usage: ./verify-contract.sh <contract-address> <network>

set -e

# Check if enough arguments provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <contract-address> [network]"
    echo "Example: $0 0x8e048A20AC9743CA1132873A0c67b660d80D870a sepolia"
    exit 1
fi

CONTRACT_ADDRESS=$1
NETWORK=${2:-sepolia}

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if API key is set
if [ -z "$ETHERSCAN_API_KEY" ]; then
    echo "❌ Error: ETHERSCAN_API_KEY not found in .env file"
    echo "Please add your Etherscan API key to .env file:"
    echo "ETHERSCAN_API_KEY=your_api_key_here"
    exit 1
fi

# Network configurations
case $NETWORK in
    mainnet)
        API_URL="https://api.etherscan.io/api"
        EXPLORER_URL="https://etherscan.io"
        ;;
    sepolia)
        API_URL="https://api-sepolia.etherscan.io/api"
        EXPLORER_URL="https://sepolia.etherscan.io"
        ;;
    polygon)
        API_URL="https://api.polygonscan.com/api"
        EXPLORER_URL="https://polygonscan.com"
        ;;
    *)
        echo "❌ Unsupported network: $NETWORK"
        echo "Supported networks: mainnet, sepolia, polygon"
        exit 1
        ;;
esac

echo "🔍 Verifying contract on $NETWORK..."
echo "📍 Contract Address: $CONTRACT_ADDRESS"
echo "🌐 API URL: $API_URL"

# Read the contract source code
CONTRACT_SOURCE=$(cat contracts/PoCRegistry.sol)

# Prepare the verification request
curl -X POST "$API_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "apikey=$ETHERSCAN_API_KEY" \
    -d "module=contract" \
    -d "action=verifysourcecode" \
    -d "contractaddress=$CONTRACT_ADDRESS" \
    -d "sourceCode=$CONTRACT_SOURCE" \
    -d "codeformat=solidity-single-file" \
    -d "contractname=PoCRegistry" \
    -d "compilerversion=v0.8.17+commit.df83b5de" \
    -d "optimizationUsed=0" \
    -d "runs=200" \
    -d "constructorArguements=" \
    -d "evmversion=london" \
    -d "licenseType=3" \
    | jq '.'

echo ""
echo "✅ Verification request submitted!"
echo "🔗 View your contract: $EXPLORER_URL/address/$CONTRACT_ADDRESS"
echo ""
echo "⏳ Verification may take a few minutes. Check the explorer link above."