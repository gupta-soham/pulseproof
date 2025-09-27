#!/bin/bash

# Script to pull Docker images with retry and timeout handling
set -e

IMAGES=(
    "postgres:14-alpine"
    "ipfs/kubo:release"
    "graphprotocol/graph-node:latest"
)

RETRY_COUNT=3
TIMEOUT=300  # 5 minutes

pull_with_retry() {
    local image=$1
    local attempt=1
    
    echo "Attempting to pull $image..."
    
    while [ $attempt -le $RETRY_COUNT ]; do
        echo "Attempt $attempt/$RETRY_COUNT for $image"
        
        if timeout $TIMEOUT docker pull --platform linux/amd64 "$image"; then
            echo "✅ Successfully pulled $image"
            return 0
        else
            echo "❌ Attempt $attempt failed for $image"
            if [ $attempt -lt $RETRY_COUNT ]; then
                echo "Waiting 30 seconds before retry..."
                sleep 30
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    echo "❌ Failed to pull $image after $RETRY_COUNT attempts"
    return 1
}

main() {
    echo "🐳 Starting Docker image pulls with retry logic..."
    echo "Images to pull: ${IMAGES[*]}"
    echo "Retry count: $RETRY_COUNT"
    echo "Timeout per attempt: ${TIMEOUT}s"
    echo "----------------------------------------"
    
    failed_images=()
    
    for image in "${IMAGES[@]}"; do
        if ! pull_with_retry "$image"; then
            failed_images+=("$image")
        fi
        echo "----------------------------------------"
    done
    
    if [ ${#failed_images[@]} -eq 0 ]; then
        echo "🎉 All images pulled successfully!"
        echo "You can now run: docker-compose up"
    else
        echo "❌ The following images failed to pull:"
        for image in "${failed_images[@]}"; do
            echo "  - $image"
        done
        echo ""
        echo "💡 Try the following troubleshooting steps:"
        echo "1. Check your internet connection"
        echo "2. Restart Docker Desktop"
        echo "3. Try using a VPN"
        echo "4. Use alternative image tags"
    fi
}

main "$@"