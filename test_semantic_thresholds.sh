#!/bin/bash

# Get JWT
JWT=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")

echo "Threshold Test Results:"
echo "======================"

# Test different thresholds
for threshold in 0.01 0.1 0.3 0.5 0.7; do
    echo ""
    echo "Threshold: $threshold"
    RESULT=$(curl -s -w "\n%{http_code}" -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=$threshold&top_k=5" \
      -H "Authorization: Bearer $JWT")
    
    HTTP_CODE=$(echo "$RESULT" | tail -1)
    BODY=$(echo "$RESULT" | head -1)
    COUNT=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', '?'))" 2>/dev/null || echo "ERROR")
    
    echo "  HTTP: $HTTP_CODE, Results: $COUNT"
done
