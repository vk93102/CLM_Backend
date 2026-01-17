#!/bin/bash

# Get JWT
JWT=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null || echo "")

if [[ -z "$JWT" ]]; then
    echo "Failed to get JWT"
    exit 1
fi

echo "======================"
echo "Semantic Search Test"
echo "======================"

# Test one specific query
echo -e "\nQuery: 'confidentiality' with threshold=0.1"
curl -s -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.1&top_k=5" \
  -H "Authorization: Bearer $JWT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Results: {data.get('count', 0)}, HTTP response: OK\")"
