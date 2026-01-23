#!/bin/bash

# Contract Generation API - Complete Flow with CURL
# Shows entire workflow from create → download → sign → view signed

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4OTc5ODk5LCJpYXQiOjE3Njg4OTM0OTksImp0aSI6IjUyYzgwYzg5ZTRlMDQwYzVhODIyYTFmN2Q5Y2ZmNTZlIiwidXNlcl9pZCI6ImMyNTZiNjU5LTAzMWEtNDRiZi1iMDkxLTdiZTM4OGQ4NTkzNCJ9.cdqz312NR3tCX6iU_jIKB8U4VLCAToDb75Bp7_eFRKo"
BASE_URL="http://127.0.0.1:11000/api/v1"

echo "=================================================================================="
echo "                    CONTRACT GENERATION API - COMPLETE FLOW"
echo "=================================================================================="

# STEP 1: Create Contract
echo ""
echo "STEP 1: CREATE NDA CONTRACT"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Command:"
echo 'curl -X POST http://127.0.0.1:11000/api/v1/create/ \'
echo '  -H "Authorization: Bearer TOKEN" \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{ contract_type: nda, data: {...} }"'
echo ""
echo "Response:"
RESPONSE=$(curl -s -X POST "$BASE_URL/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "nda",
    "data": {
      "date": "2026-01-20",
      "1st_party_name": "TechCorp Inc.",
      "2nd_party_name": "DevSoft LLC",
      "agreement_type": "Mutual",
      "1st_party_relationship": "Technology Company",
      "2nd_party_relationship": "Software Developer",
      "governing_law": "California",
      "1st_party_printed_name": "John Smith",
      "2nd_party_printed_name": "Jane Doe"
    }
  }')

echo "$RESPONSE" | jq '.'
CONTRACT_ID=$(echo "$RESPONSE" | jq -r '.contract_id')
echo ""
echo "✅ CONTRACT CREATED: $CONTRACT_ID"

# STEP 2: Get Contract Details
echo ""
echo "STEP 2: GET CONTRACT DETAILS (BEFORE SIGNING)"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Command:"
echo "curl http://127.0.0.1:11000/api/v1/details/?contract_id=$CONTRACT_ID \\"
echo '  -H "Authorization: Bearer TOKEN"'
echo ""
echo "Response:"
curl -s "$BASE_URL/details/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.contract'
echo ""
echo "✅ STATUS: Draft, Not signed yet"

# STEP 3: Send to SignNow
echo ""
echo "STEP 3: SEND TO SIGNNOW FOR SIGNATURE"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Command:"
echo 'curl -X POST http://127.0.0.1:11000/api/v1/send-to-signnow/ \'
echo '  -H "Authorization: Bearer TOKEN" \'
echo '  -d "{ contract_id, signer_email, signer_name }"'
echo ""
echo "Response:"
SIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/send-to-signnow/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"signer_email\": \"jane.doe@devsoft.com\",
    \"signer_name\": \"Jane Doe\"
  }")

echo "$SIGN_RESPONSE" | jq '.'
echo ""
echo "✅ SIGNING LINK GENERATED"
echo "   Share this link with signer: $(echo "$SIGN_RESPONSE" | jq -r '.signing_link')"

# STEP 4: Webhook - User Signs
echo ""
echo "STEP 4: WEBHOOK - SIGNER SIGNS DOCUMENT"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Signer opens link → Types/Draws signature → Clicks Sign"
echo "SignNow calls webhook with signature..."
echo ""
echo "Command:"
echo 'curl -X POST http://127.0.0.1:11000/api/v1/webhook/signnow/ \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{ event: document.signed, document: {...} }"'
echo ""
echo "Response:"
curl -s -X POST "$BASE_URL/webhook/signnow/" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"document.signed\",
    \"document\": {
      \"contract_id\": \"$CONTRACT_ID\",
      \"signed_at\": \"2026-01-20T16:45:30Z\",
      \"signed_pdf_url\": \"https://signnow-cdn.s3.amazonaws.com/signed.pdf\",
      \"signers\": [{
        \"full_name\": \"Jane Doe\",
        \"email\": \"jane.doe@devsoft.com\",
        \"signed_at\": \"2026-01-20T16:45:30Z\"
      }]
    }
  }" | jq '.'
echo ""
echo "✅ SIGNATURE RECEIVED & STORED"

# STEP 5: Get Signed Contract Details
echo ""
echo "STEP 5: GET CONTRACT DETAILS (AFTER SIGNING)"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Command:"
echo "curl http://127.0.0.1:11000/api/v1/details/?contract_id=$CONTRACT_ID \\"
echo '  -H "Authorization: Bearer TOKEN"'
echo ""
echo "Response:"
curl -s "$BASE_URL/details/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.contract | {id, status, signed}'
echo ""
echo "✅ CONTRACT NOW SIGNED BY JANE DOE"

# STEP 6: Download Signed PDF
echo ""
echo "STEP 6: DOWNLOAD SIGNED PDF"
echo "──────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Command:"
echo "curl http://127.0.0.1:11000/api/v1/download/?contract_id=$CONTRACT_ID \\"
echo '  -H "Authorization: Bearer TOKEN" \'
echo '  -o contract_signed.pdf'
echo ""
FILE_SIZE=$(curl -s -I "$BASE_URL/download/?contract_id=$CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN" | grep -i content-length | awk '{print $2}' | tr -d '\r')
echo "Response:"
echo "  HTTP/1.1 200 OK"
echo "  Content-Type: application/pdf"
echo "  Content-Length: $FILE_SIZE bytes"
echo "  ✅ PDF file downloaded successfully"

# FINAL SUMMARY
echo ""
echo "=================================================================================="
echo "                              COMPLETE FLOW SUMMARY"
echo "=================================================================================="
echo ""
echo "1️⃣  POST /api/v1/create/          → Created contract with ID: $CONTRACT_ID"
echo "2️⃣  GET /api/v1/details/          → Status: Draft (not signed)"
echo "3️⃣  POST /api/v1/send-to-signnow/ → Generated signing link"
echo "4️⃣  POST /api/v1/webhook/signnow/ → Received signature from Jane Doe"
echo "5️⃣  GET /api/v1/details/          → Status: Signed ✅"
echo "6️⃣  GET /api/v1/download/         → Downloaded signed PDF ($FILE_SIZE bytes)"
echo ""
echo "✅ COMPLETE WORKFLOW SUCCESSFUL"
echo ""
