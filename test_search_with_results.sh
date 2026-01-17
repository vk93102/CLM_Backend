#!/bin/bash

# Get JWT
echo "Getting JWT..."
JWT_RESPONSE=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}')

JWT=$(echo "$JWT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null || echo "")

if [[ -z "$JWT" ]]; then
    echo "✗ Failed to get JWT"
    echo "Response: $JWT_RESPONSE"
    exit 1
fi

echo "✓ JWT obtained: ${JWT:0:50}..."

# Test semantic search
echo -e "\n=== TEST 1: Semantic Search for 'confidentiality' ==="
curl -s -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.5&top_k=10" \
  -H "Authorization: Bearer $JWT" | python3 -m json.tool 2>&1

echo -e "\n=== TEST 2: Keyword Search for 'payment' ==="
curl -s -X GET "http://localhost:11000/api/search/keyword/?q=payment&limit=10" \
  -H "Authorization: Bearer $JWT" | python3 -m json.tool 2>&1
