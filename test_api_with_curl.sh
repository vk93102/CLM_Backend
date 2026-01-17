#!/bin/bash

echo "========================================"
echo "API Endpoint Testing with cURL"
echo "========================================"
echo ""

# Check if server is running
echo "[1] Checking server status..."
HEALTH=$(curl -s http://localhost:8000/api/search/stats/ 2>&1)
if echo "$HEALTH" | grep -q "Authentication"; then
    echo "✓ Server is running and responding"
else
    echo "✗ Server issue"
    echo "Response: $HEALTH"
    exit 1
fi

# Test endpoints
echo ""
echo "[2] Testing available endpoints..."
echo "  GET /api/search/ (list)"
curl -s -H "Authorization: Bearer invalid_token" http://localhost:8000/api/search/ 2>&1 | head -5
echo ""

echo "  GET /api/documents/ (list)"
curl -s -H "Authorization: Bearer invalid_token" http://localhost:8000/api/documents/ 2>&1 | head -5
echo ""

echo "  GET /api/repository/ (list)"
curl -s -H "Authorization: Bearer invalid_token" http://localhost:8000/api/repository/ 2>&1 | head -5
echo ""

echo "========================================"
echo "Tests Complete"
echo "========================================"
