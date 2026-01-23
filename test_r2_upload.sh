#!/bin/bash

# Cloudflare R2 Upload - Quick Test Script
# Tests all R2 upload and download endpoints

BASE_URL="http://localhost:11000"
API_BASE="$BASE_URL/api/contracts"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Cloudflare R2 Integration Test Suite"
echo "=================================================="
echo ""

# Step 1: Login and get token
echo "${YELLOW}Step 1: Authentication${NC}"
echo "Logging in..."

# Replace with your test credentials
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token // .access')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "${RED}✗ Login failed. Please check credentials.${NC}"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "${GREEN}✓ Login successful${NC}"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Create test file
echo "Creating test PDF file..."
echo "%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Contract Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000315 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
408
%%EOF" > test_contract.pdf

echo "${GREEN}✓ Test PDF created${NC}"
echo ""

# Step 2: Simple Document Upload
echo "${YELLOW}Step 2: Simple Document Upload${NC}"
echo "Uploading test document to Cloudflare R2..."

UPLOAD_RESPONSE=$(curl -s -X POST "$API_BASE/upload-document/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_contract.pdf" \
  -F "filename=TestContract_$(date +%Y%m%d).pdf")

echo "Response:"
echo $UPLOAD_RESPONSE | jq .

SUCCESS=$(echo $UPLOAD_RESPONSE | jq -r '.success')
if [ "$SUCCESS" == "true" ]; then
  echo "${GREEN}✓ Document uploaded successfully${NC}"
  DOWNLOAD_URL=$(echo $UPLOAD_RESPONSE | jq -r '.download_url')
  R2_KEY=$(echo $UPLOAD_RESPONSE | jq -r '.r2_key')
  FILE_SIZE=$(echo $UPLOAD_RESPONSE | jq -r '.file_size')
  echo "  - R2 Key: $R2_KEY"
  echo "  - File Size: $FILE_SIZE bytes"
  echo "  - Download URL: ${DOWNLOAD_URL:0:80}..."
else
  echo "${RED}✗ Upload failed${NC}"
fi
echo ""

# Step 3: Upload Contract Document with Record Creation
echo "${YELLOW}Step 3: Upload Contract Document (with DB record)${NC}"
echo "Uploading contract with database record creation..."

CONTRACT_UPLOAD_RESPONSE=$(curl -s -X POST "$API_BASE/upload-contract-document/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_contract.pdf" \
  -F "create_contract=true" \
  -F "title=Test Service Agreement - $(date +%Y-%m-%d)" \
  -F "contract_type=service_agreement" \
  -F "counterparty=Test Company Inc")

echo "Response:"
echo $CONTRACT_UPLOAD_RESPONSE | jq .

SUCCESS=$(echo $CONTRACT_UPLOAD_RESPONSE | jq -r '.success')
if [ "$SUCCESS" == "true" ]; then
  echo "${GREEN}✓ Contract uploaded and record created${NC}"
  CONTRACT_ID=$(echo $CONTRACT_UPLOAD_RESPONSE | jq -r '.contract_id')
  CONTRACT_TITLE=$(echo $CONTRACT_UPLOAD_RESPONSE | jq -r '.contract_title')
  CONTRACT_R2_KEY=$(echo $CONTRACT_UPLOAD_RESPONSE | jq -r '.r2_key')
  echo "  - Contract ID: $CONTRACT_ID"
  echo "  - Title: $CONTRACT_TITLE"
  echo "  - R2 Key: $CONTRACT_R2_KEY"
else
  echo "${RED}✗ Contract upload failed${NC}"
fi
echo ""

# Step 4: Get Download URL by R2 Key
if [ ! -z "$R2_KEY" ] && [ "$R2_KEY" != "null" ]; then
  echo "${YELLOW}Step 4: Get Download URL by R2 Key${NC}"
  echo "Generating new download URL for R2 key: $R2_KEY"
  
  URL_RESPONSE=$(curl -s -X GET "$API_BASE/document-download-url/?r2_key=$R2_KEY&expiration=7200" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "Response:"
  echo $URL_RESPONSE | jq .
  
  SUCCESS=$(echo $URL_RESPONSE | jq -r '.success')
  if [ "$SUCCESS" == "true" ]; then
    echo "${GREEN}✓ Download URL generated${NC}"
    NEW_DOWNLOAD_URL=$(echo $URL_RESPONSE | jq -r '.download_url')
    EXPIRATION=$(echo $URL_RESPONSE | jq -r '.expiration_seconds')
    echo "  - Expiration: $EXPIRATION seconds (2 hours)"
    echo "  - URL: ${NEW_DOWNLOAD_URL:0:80}..."
  else
    echo "${RED}✗ Failed to generate download URL${NC}"
  fi
  echo ""
fi

# Step 5: Get Contract Download URL by ID
if [ ! -z "$CONTRACT_ID" ] && [ "$CONTRACT_ID" != "null" ]; then
  echo "${YELLOW}Step 5: Get Contract Download URL by ID${NC}"
  echo "Getting download URL for contract ID: $CONTRACT_ID"
  
  CONTRACT_URL_RESPONSE=$(curl -s -X GET "$API_BASE/$CONTRACT_ID/download-url/" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "Response:"
  echo $CONTRACT_URL_RESPONSE | jq .
  
  SUCCESS=$(echo $CONTRACT_URL_RESPONSE | jq -r '.success')
  if [ "$SUCCESS" == "true" ]; then
    echo "${GREEN}✓ Contract download URL retrieved${NC}"
    CONTRACT_DOWNLOAD_URL=$(echo $CONTRACT_URL_RESPONSE | jq -r '.download_url')
    VERSION=$(echo $CONTRACT_URL_RESPONSE | jq -r '.version_number')
    echo "  - Version: $VERSION"
    echo "  - URL: ${CONTRACT_DOWNLOAD_URL:0:80}..."
  else
    echo "${RED}✗ Failed to get contract download URL${NC}"
  fi
  echo ""
fi

# Step 6: Test Download (verify URL works)
if [ ! -z "$DOWNLOAD_URL" ] && [ "$DOWNLOAD_URL" != "null" ]; then
  echo "${YELLOW}Step 6: Verify Download URL Works${NC}"
  echo "Attempting to download file from Cloudflare R2..."
  
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DOWNLOAD_URL")
  
  if [ "$HTTP_CODE" == "200" ]; then
    echo "${GREEN}✓ Download URL is valid and working${NC}"
    echo "  - HTTP Status: $HTTP_CODE OK"
  else
    echo "${RED}✗ Download failed${NC}"
    echo "  - HTTP Status: $HTTP_CODE"
  fi
  echo ""
fi

# Cleanup
echo "${YELLOW}Cleanup${NC}"
rm -f test_contract.pdf
echo "${GREEN}✓ Test file removed${NC}"
echo ""

# Summary
echo "=================================================="
echo "Test Summary"
echo "=================================================="
echo "${GREEN}Tests completed!${NC}"
echo ""
echo "Tested endpoints:"
echo "  1. POST /api/contracts/upload-document/"
echo "  2. POST /api/contracts/upload-contract-document/"
echo "  3. GET  /api/contracts/document-download-url/"
echo "  4. GET  /api/contracts/<id>/download-url/"
echo ""

if [ ! -z "$CONTRACT_ID" ] && [ "$CONTRACT_ID" != "null" ]; then
  echo "📋 Created Contract:"
  echo "  - ID: $CONTRACT_ID"
  echo "  - Title: $CONTRACT_TITLE"
  echo ""
  echo "You can view this contract at:"
  echo "  GET $API_BASE/$CONTRACT_ID/"
fi

if [ ! -z "$DOWNLOAD_URL" ]; then
  echo ""
  echo "📥 Download URLs (valid for limited time):"
  echo "  Simple document: ${DOWNLOAD_URL:0:80}..."
  if [ ! -z "$CONTRACT_DOWNLOAD_URL" ]; then
    echo "  Contract: ${CONTRACT_DOWNLOAD_URL:0:80}..."
  fi
fi

echo ""
echo "${GREEN}All tests completed successfully!${NC}"
echo "=================================================="
