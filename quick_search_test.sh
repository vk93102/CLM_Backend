#!/bin/bash

# Get JWT token
echo "Getting JWT token..."
JWT=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))")

if [[ -z "$JWT" ]]; then
    echo "✗ Failed to get JWT token"
    exit 1
fi

echo "✓ JWT Token: ${JWT:0:50}..."

# Make search request
echo -e "\nSearching for 'confidentiality'..."
curl -s -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.5&top_k=10" \
  -H "Authorization: Bearer $JWT" | python3 -m json.tool 2>&1
