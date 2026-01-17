#!/bin/bash

# AI Endpoints Quick Start Testing Guide
# This script provides curl commands to test all three AI endpoints

set -e

# Configuration
BASE_URL="http://localhost:8000/api/v1"
JWT_TOKEN="${JWT_TOKEN:-your-jwt-token-here}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CLM AI Endpoints Testing Suite ===${NC}\n"

# Check if JWT token is provided
if [ "$JWT_TOKEN" = "your-jwt-token-here" ]; then
    echo -e "${RED}Error: JWT_TOKEN not set${NC}"
    echo "Usage: JWT_TOKEN='your-token' bash test_ai_endpoints.sh"
    exit 1
fi

# Test 1: Initialize Anchor Clauses
echo -e "${BLUE}[1] Initializing Anchor Clauses${NC}"
echo "Command: python manage.py initialize_anchors"
echo ""
echo -e "${YELLOW}Manual Setup:${NC}"
echo "python manage.py initialize_anchors --clear"
echo ""

# Test 2: Draft Generation
echo -e "${BLUE}[2] Testing Draft Generation${NC}"
echo -e "${YELLOW}Request:${NC}"
echo "curl -X POST $BASE_URL/ai/generate/draft/ \\"
echo "  -H 'Authorization: Bearer \$JWT_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{...}'"
echo ""

DRAFT_RESPONSE=$(curl -s -X POST "$BASE_URL/ai/generate/draft/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "Service Agreement",
    "input_params": {
      "parties": ["Acme Corp", "Widget Inc"],
      "contract_value": 100000,
      "start_date": "2024-02-01",
      "end_date": "2025-02-01",
      "scope": "Cloud infrastructure services"
    }
  }')

echo -e "${YELLOW}Response:${NC}"
echo "$DRAFT_RESPONSE" | jq '.' 2>/dev/null || echo "$DRAFT_RESPONSE"
echo ""

# Extract task_id for status polling
TASK_ID=$(echo "$DRAFT_RESPONSE" | jq -r '.id' 2>/dev/null || echo "")

if [ -z "$TASK_ID" ] || [ "$TASK_ID" = "null" ]; then
    echo -e "${RED}Failed to extract task_id. Check your JWT token and API access.${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Draft generation task created: $TASK_ID${NC}"
    echo ""
    
    # Test 3: Check Status
    echo -e "${BLUE}[3] Polling Task Status${NC}"
    echo "Task ID: $TASK_ID"
    echo ""
    
    for i in {1..5}; do
        echo -e "${YELLOW}Attempt $i/5:${NC}"
        
        STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/ai/generate/status/$TASK_ID/" \
          -H "Authorization: Bearer $JWT_TOKEN" \
          -H "Content-Type: application/json")
        
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")
        echo "Status: $STATUS"
        
        if [ "$STATUS" = "completed" ]; then
            echo -e "${GREEN}✓ Generation complete!${NC}"
            echo ""
            echo "Generated text length: $(echo "$STATUS_RESPONSE" | jq '.generated_text | length' 2>/dev/null || echo 'N/A')"
            echo "Citations count: $(echo "$STATUS_RESPONSE" | jq '.citations | length' 2>/dev/null || echo 'N/A')"
            echo ""
            break
        elif [ "$STATUS" = "failed" ]; then
            echo -e "${RED}✗ Generation failed!${NC}"
            echo "Error: $(echo "$STATUS_RESPONSE" | jq -r '.error_message' 2>/dev/null)"
            echo ""
            break
        elif [ "$STATUS" = "processing" ]; then
            echo "Still processing... waiting 3 seconds"
            sleep 3
        else
            echo "Waiting for processing to start..."
            sleep 2
        fi
    done
fi

echo ""

# Test 4: Metadata Extraction (requires a document_id)
echo -e "${BLUE}[4] Testing Metadata Extraction${NC}"
echo -e "${YELLOW}Note: Requires a valid document_id from your system${NC}"
echo ""
echo "Command:"
echo "curl -X POST $BASE_URL/ai/extract/metadata/ \\"
echo "  -H 'Authorization: Bearer \$JWT_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"document_id\": \"your-document-uuid\"}'"
echo ""

# Test 5: Clause Classification
echo -e "${BLUE}[5] Testing Clause Classification${NC}"
echo -e "${YELLOW}Request:${NC}"
echo "curl -X POST $BASE_URL/ai/classify/ \\"
echo "  -H 'Authorization: Bearer \$JWT_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{...}'"
echo ""

CLASSIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/ai/classify/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The parties agree to maintain the confidentiality of all non-public information disclosed in connection with this Agreement. Confidential Information includes but is not limited to technical data, business plans, customer lists, and financial information. Each party agrees not to disclose Confidential Information to third parties without prior written consent, except as required by law."
  }')

echo -e "${YELLOW}Response:${NC}"
echo "$CLASSIFY_RESPONSE" | jq '.' 2>/dev/null || echo "$CLASSIFY_RESPONSE"
echo ""

LABEL=$(echo "$CLASSIFY_RESPONSE" | jq -r '.label' 2>/dev/null || echo "")
CONFIDENCE=$(echo "$CLASSIFY_RESPONSE" | jq -r '.confidence' 2>/dev/null || echo "")

if [ ! -z "$LABEL" ] && [ "$LABEL" != "null" ]; then
    echo -e "${GREEN}✓ Classified as: $LABEL (confidence: $CONFIDENCE)${NC}"
    echo ""
fi

# Summary
echo -e "${BLUE}=== Testing Summary ===${NC}"
echo ""
echo "Endpoints tested:"
echo "  ✓ POST /api/v1/ai/generate/draft/ - Draft generation"
echo "  ✓ GET /api/v1/ai/generate/status/{task_id}/ - Status polling"
echo "  ○ POST /api/v1/ai/extract/metadata/ - Metadata extraction (manual)"
echo "  ✓ POST /api/v1/ai/classify/ - Clause classification"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Set up Celery worker: celery -A clm_backend worker -l info"
echo "2. Set up Redis: redis-server"
echo "3. Initialize anchors: python manage.py initialize_anchors"
echo "4. Run full test suite with actual documents"
echo ""

echo -e "${YELLOW}Documentation:${NC}"
echo "See AI_ENDPOINTS_COMPLETE.md for detailed API documentation"
echo ""
