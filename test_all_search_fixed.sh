#!/bin/bash

# Get JWT
JWT=$(curl -s -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))" 2>/dev/null)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ALL SEARCH ENDPOINTS - REAL DATA TEST               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Keyword Search
echo "[1] KEYWORD SEARCH"
echo "───────────────────────────────────────────────────────────"
KEYWORD=$(curl -s -X GET "http://localhost:11000/api/search/keyword/?q=confidentiality&limit=10" \
  -H "Authorization: Bearer $JWT")
COUNT=$(echo "$KEYWORD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
echo "Results: $COUNT"
if [[ $COUNT -gt 0 ]]; then
    echo "✅ WORKING - Returns real data"
    echo "$KEYWORD" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d['results'][0]; print(f\"  Sample: {r.get('filename')} (chunk: {r.get('chunk_number')})\")" 2>/dev/null
fi
echo ""

# Test 2: Semantic Search (with new lower threshold)
echo "[2] SEMANTIC SEARCH"
echo "───────────────────────────────────────────────────────────"
SEMANTIC=$(curl -s -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.2&top_k=10" \
  -H "Authorization: Bearer $JWT")
COUNT=$(echo "$SEMANTIC" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
echo "Results: $COUNT"
if [[ $COUNT -gt 0 ]]; then
    echo "✅ WORKING - Returns real data"
    echo "$SEMANTIC" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d['results'][0]; print(f\"  Sample: {r.get('filename')} (similarity: {r.get('similarity_score')})\")" 2>/dev/null
else
    echo "⚠ Still returning 0 results"
fi
echo ""

# Test 3: Advanced Search (newly created)
echo "[3] ADVANCED SEARCH"
echo "───────────────────────────────────────────────────────────"
ADVANCED=$(curl -s -X POST http://localhost:11000/api/search/advanced/ \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"query": "confidentiality", "filters": {"document_type": "contract"}, "top_k": 10}')
COUNT=$(echo "$ADVANCED" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null)
echo "Results: $COUNT"
if [[ $COUNT -gt 0 ]]; then
    echo "✅ WORKING - Returns real data"
    echo "$ADVANCED" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d['results'][0]; print(f\"  Sample: {r.get('filename')} (chunk: {r.get('chunk_number')})\")" 2>/dev/null
else
    echo "⚠ Still returning 0 results"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
