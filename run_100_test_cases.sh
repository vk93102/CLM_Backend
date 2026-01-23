#!/bin/bash

set -euo pipefail

##############################################################################
# AUTHENTICATED PRODUCTION TEST SUITE - 100 TEST CASES
# Executes full template, clause, and contract flows against port 11000
# Requires the Django API server to be running with valid environment config
##############################################################################

API_BASE="http://localhost:11000/api/v1"
AUTH_BASE="http://localhost:11000/api/auth"
REPORT="/dev/null"  # Disk full - skip report generation
TEST_EMAIL="${TEST_EMAIL:-automation_user@example.com}"
TEST_PASSWORD="${TEST_PASSWORD:-Str0ngP@ssword1!}"

# Export for Python subprocess
export TEST_EMAIL
export TEST_PASSWORD

TEST_COUNT=0
PASS=0
FAIL=0
LAST_BODY=""
LAST_STATUS=""
ACCESS_TOKEN=""
REFRESH_TOKEN=""
USER_ID=""
TENANT_ID=""
CLAUSE_DB_ID=""
CLAUSE_CODE=""
SECOND_CLAUSE_ID=""
TEMPLATE_ID=""
SECOND_TEMPLATE_ID=""
CONTRACT_ID=""
CLONE_CONTRACT_ID=""

# Skip report generation due to disk space
# cat > "$REPORT" << 'EOF'
# # COMPREHENSIVE TEST SUITE - 100 TEST CASES
# ## Production-Level API Testing Report
# ---
# 
# EOF

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_test() {
	local num=$1
	local name=$2
	echo -e "${BLUE}[TEST $num] $name${NC}"
	# echo "## Test $num: $name" >> "$REPORT"
	# echo "" >> "$REPORT"
}

log_response() {
	local method=$1
	local endpoint=$2
	local status=$3
	local response=$4

	# Disabled report writes to avoid disk full
	# echo "### Request" >> "$REPORT"
	# echo "\`\`\`" >> "$REPORT"
	# echo "$method $endpoint" >> "$REPORT"
	# echo "\`\`\`" >> "$REPORT"
	# echo "" >> "$REPORT"
	# echo "### Status Code: $status" >> "$REPORT"
	# echo "" >> "$REPORT"
	# echo "### Response" >> "$REPORT"
	# echo "\`\`\`json" >> "$REPORT"
	# echo "$response" | jq '.' >> "$REPORT" 2>/dev/null || echo "$response" >> "$REPORT"
	# echo "\`\`\`" >> "$REPORT"
	# echo "" >> "$REPORT"
}

pass() {
	((PASS++))
	echo -e "${GREEN}✓ PASS${NC}"
}

fail() {
	((FAIL++))
	echo -e "${RED}✗ FAIL${NC}"
}

run_json_test() {
	local method=$1
	local endpoint=$2
	local name=$3
	local data=${4:-}
	local expected=${5:-200}
	local auth_mode=${6:-auth}
	local base=${7:-$API_BASE}

	((TEST_COUNT++))
	log_test $TEST_COUNT "$name"

	local url
	if [[ "$endpoint" == http* ]]; then
		url="$endpoint"
	else
		url="$base$endpoint"
	fi

	local curl_args=("-s" "-w" "\n%{http_code}" "-X" "$method")
	if [[ -n "$data" ]]; then
		curl_args+=("-H" "Content-Type: application/json" "-d" "$data")
	fi
	if [[ "$auth_mode" != "noauth" ]]; then
		curl_args+=("-H" "Authorization: Bearer $ACCESS_TOKEN")
	fi

	local response
	response=$(curl "${curl_args[@]}" "$url")
	local status="${response##*$'\n'}"
	local body="${response%$'\n'$status}"

	log_response "$method" "$url" "$status" "$body"

	# Pretty print JSON response
	if command -v jq &> /dev/null && [[ -n "$body" ]]; then
		echo "$body" | jq . 2>/dev/null || echo "$body"
	else
		echo "$body"
	fi
	echo ""

	LAST_BODY="$body"
	LAST_STATUS="$status"

	if [[ "$status" == "$expected" ]]; then
		pass
	else
		fail
	fi
}

ensure_automation_user() {
	local result
	result=$(python3 <<'PY'
import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

email = os.environ['TEST_EMAIL']
password = os.environ['TEST_PASSWORD']
User = get_user_model()
user = User.objects.filter(email=email).first()
if user is None:
	user = User(email=email)
if not user.first_name:
	user.first_name = 'Automation'
if not user.last_name:
	user.last_name = 'Tester'
user.is_active = True
user.set_password(password)
user.save()
print(json.dumps({
	'user_id': str(user.user_id),
	'tenant_id': str(user.tenant_id)
}))
PY
	)
	USER_ID=$(echo "$result" | jq -r '.user_id')
	TENANT_ID=$(echo "$result" | jq -r '.tenant_id')
}

ensure_automation_user

echo -e "${BLUE}=== SECTION 1: SESSION & CONNECTIVITY ===${NC}"

run_json_test "GET" "/health/" "Health check - server running" "" 200 "noauth"
run_json_test "POST" "/login/" "Authenticate automation user" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" 200 "noauth" "$AUTH_BASE"
ACCESS_TOKEN=$(echo "$LAST_BODY" | jq -r '.access')
REFRESH_TOKEN=$(echo "$LAST_BODY" | jq -r '.refresh')
run_json_test "POST" "/refresh/" "Refresh JWT token" "{\"refresh\":\"$REFRESH_TOKEN\"}" 200 "noauth" "$AUTH_BASE"
ACCESS_TOKEN=$(echo "$LAST_BODY" | jq -r '.access')
REFRESH_TOKEN=$(echo "$LAST_BODY" | jq -r '.refresh')
run_json_test "GET" "/me/" "Fetch current user profile" "" 200 "auth" "$AUTH_BASE"
run_json_test "GET" "/contract-templates/" "List templates (initial)" ""
run_json_test "GET" "/contracts/" "List contracts (initial)" ""
run_json_test "GET" "/clauses/" "List clauses (initial)" ""
run_json_test "GET" "/generation-jobs/" "List generation jobs (initial)" ""
run_json_test "GET" "/contracts/statistics/" "Fetch contract statistics" ""
run_json_test "GET" "/contracts/recent/?limit=5" "Fetch recent contracts" ""

echo -e "${BLUE}=== SECTION 2: CLAUSE OPERATIONS ===${NC}"

CLAUSE_CODE="CL-$(uuidgen | tr '[:lower:]' '[:upper:]' | cut -c1-8)"
CLAUSE_PAYLOAD=$(jq -n --arg clause_id "$CLAUSE_CODE" '{
	clause_id: $clause_id,
	name: "Automation Clause",
	contract_type: "MSA",
	content: "Confidentiality obligations for {{counterparty}}.",
	status: "published",
	is_mandatory: true
}')
run_json_test "POST" "/clauses/" "Create primary clause" "$CLAUSE_PAYLOAD" 201
CLAUSE_DB_ID=$(echo "$LAST_BODY" | jq -r '.id')

run_json_test "GET" "/clauses/$CLAUSE_DB_ID/" "Retrieve primary clause detail" ""
run_json_test "GET" "/clauses/" "List clauses after creation" ""
run_json_test "GET" "/clauses/?contract_type=MSA" "Filter clauses by contract type" ""
run_json_test "GET" "/clauses/?status=published" "Filter clauses by status" ""
run_json_test "GET" "/clauses/?search=Automation" "Search clauses by name" ""
run_json_test "GET" "/clauses/?clause_id=$CLAUSE_CODE" "Filter clauses by clause_id" ""
run_json_test "GET" "/clauses/?version=1" "Filter clauses by version" ""
UPDATE_CLAUSE_PAYLOAD=$(jq -n '{
	name: "Automation Clause - Updated",
	content: "Updated confidentiality obligations for {{counterparty}}.",
	is_mandatory: true
}')
run_json_test "PATCH" "/clauses/$CLAUSE_DB_ID/" "Patch clause details" "$UPDATE_CLAUSE_PAYLOAD" ""
run_json_test "GET" "/clauses/$CLAUSE_DB_ID/" "Confirm clause patch" ""
SECOND_CLAUSE_CODE="CL-$(uuidgen | tr '[:lower:]' '[:upper:]' | cut -c1-8)"
SECOND_CLAUSE_PAYLOAD=$(jq -n --arg clause_id "$SECOND_CLAUSE_CODE" '{
	clause_id: $clause_id,
	name: "Automation Clause Variant",
	contract_type: "MSA",
	content: "Variant clause content.",
	status: "published",
	is_mandatory: false
}')
run_json_test "POST" "/clauses/" "Create secondary clause" "$SECOND_CLAUSE_PAYLOAD" 201
SECOND_CLAUSE_ID=$(echo "$LAST_BODY" | jq -r '.id')
run_json_test "GET" "/clauses/$SECOND_CLAUSE_ID/" "Retrieve secondary clause" ""
run_json_test "GET" "/clauses/?page=1&page_size=2" "Paginate clauses" ""
ALT_REQUEST=$(jq -n '{
	contract_type: "MSA",
	contract_value: 500000,
	counterparty: "Acme Corp"
}')
run_json_test "POST" "/clauses/$CLAUSE_DB_ID/alternatives/" "Request clause alternatives" "$ALT_REQUEST" ""
run_json_test "POST" "/clauses/bulk-suggestions/" "Bulk clause suggestions (empty)" '{"contract_ids": []}'
run_json_test "GET" "/clauses/" "List clauses after bulk suggestions" ""

echo -e "${BLUE}=== SECTION 3: TEMPLATE OPERATIONS ===${NC}"

TEMPLATE_NAME="Automation Template $(uuidgen | cut -c1-6)"
TEMPLATE_PAYLOAD=$(jq -n --arg name "$TEMPLATE_NAME" --arg clause "$CLAUSE_CODE" '{
	name: $name,
	contract_type: "MSA",
	description: "Template generated by test harness",
	status: "published",
	r2_key: "templates/test.docx",
	merge_fields: ["counterparty", "value", "start_date", "end_date"],
	mandatory_clauses: [$clause],
	business_rules: {}
}')
run_json_test "POST" "/contract-templates/" "Create primary contract template" "$TEMPLATE_PAYLOAD" 201
TEMPLATE_ID=$(echo "$LAST_BODY" | jq -r '.id')

run_json_test "GET" "/contract-templates/$TEMPLATE_ID/" "Retrieve template detail" ""
run_json_test "GET" "/contract-templates/" "List contract templates" ""
run_json_test "GET" "/contract-templates/?contract_type=MSA" "Filter templates by contract type" ""
run_json_test "GET" "/contract-templates/?status=published" "Filter templates by status" ""
run_json_test "GET" "/contract-templates/?search=Automation" "Search templates" ""
run_json_test "GET" "/contract-templates/?page=1&page_size=5" "Paginate templates (page 1)" ""
run_json_test "GET" "/contract-templates/?page=2&page_size=5" "Paginate templates (page 2)" ""
PATCH_TEMPLATE_PAYLOAD=$(jq -n '{
	description: "Updated template description"
}')
run_json_test "PATCH" "/contract-templates/$TEMPLATE_ID/" "Patch template description" "$PATCH_TEMPLATE_PAYLOAD" ""
run_json_test "GET" "/contract-templates/$TEMPLATE_ID/" "Confirm template patch" ""
SECOND_TEMPLATE_NAME="Automation Template B $(uuidgen | cut -c1-6)"
SECOND_TEMPLATE_PAYLOAD=$(jq -n --arg name "$SECOND_TEMPLATE_NAME" '{
	name: $name,
	contract_type: "MSA",
	description: "Draft template for testing",
	status: "draft",
	r2_key: "templates/test_b.docx",
	merge_fields: ["counterparty"],
	mandatory_clauses: [],
	business_rules: {}
}')
run_json_test "POST" "/contract-templates/" "Create secondary template (draft)" "$SECOND_TEMPLATE_PAYLOAD" 201
SECOND_TEMPLATE_ID=$(echo "$LAST_BODY" | jq -r '.id')
PATCH_SECOND_TEMPLATE_PAYLOAD=$(jq -n '{
	description: "Draft template updated"
}')
run_json_test "PATCH" "/contract-templates/$SECOND_TEMPLATE_ID/" "Patch secondary template" "$PATCH_SECOND_TEMPLATE_PAYLOAD" ""
run_json_test "GET" "/contract-templates/$SECOND_TEMPLATE_ID/" "Retrieve secondary template" ""
run_json_test "GET" "/contract-templates/?status=draft" "List draft templates" ""
run_json_test "GET" "/contract-templates/?status=published" "List published templates" ""
run_json_test "GET" "/contract-templates/?page_size=1" "Paginate templates page_size=1" ""
run_json_test "GET" "/contract-templates/?page_size=2" "Paginate templates page_size=2" ""
run_json_test "GET" "/contract-templates/?ordering=created_at" "Order templates by created_at" ""
run_json_test "GET" "/contract-templates/?search=Nonexistent" "Search templates with no results" ""
run_json_test "GET" "/contract-templates/?contract_type=UNKNOWN" "Filter templates by unknown type" ""
run_json_test "GET" "/contract-templates/?status=archived" "Filter templates archived" ""
run_json_test "OPTIONS" "/contract-templates/" "OPTIONS contract templates" "" 200
run_json_test "GET" "/contract-templates/?contract_type=MSA&status=published" "Filter templates by type+status" ""
run_json_test "GET" "/contract-templates/?name=$TEMPLATE_NAME" "Filter templates by name" ""
run_json_test "GET" "/contract-templates/?page=1&page_size=5&search=Automation" "Search templates paginated" ""
run_json_test "GET" "/contract-templates/?page=1&page_size=5&status=published" "Paginate published templates" ""

echo -e "${BLUE}=== SECTION 4: CONTRACT OPERATIONS ===${NC}"

STRUCTURED_INPUTS=$(jq -n '{
	counterparty: "Acme Corp",
	value: 250000,
	start_date: "2026-01-20",
	end_date: "2027-01-19"
}')
CONTRACT_PAYLOAD=$(jq -n --arg template "$TEMPLATE_ID" --arg clause "$CLAUSE_CODE" --argjson inputs "$STRUCTURED_INPUTS" '{
	template_id: $template,
	structured_inputs: $inputs,
	user_instructions: "Generate standard contract",
	title: "Automation Contract",
	selected_clauses: [$clause]
}')
run_json_test "POST" "/contracts/generate/" "Generate contract from template" "$CONTRACT_PAYLOAD" 201
CONTRACT_ID=$(echo "$LAST_BODY" | jq -r '.contract.id')

run_json_test "GET" "/contracts/$CONTRACT_ID/" "Retrieve contract detail" ""
run_json_test "GET" "/contracts/" "List contracts after generation" ""
run_json_test "GET" "/contracts/?status=draft" "Filter contracts by status" ""
run_json_test "GET" "/contracts/?contract_type=MSA" "Filter contracts by type" ""
run_json_test "GET" "/contracts/?search=Automation" "Search contracts by title" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/" "List contract versions" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/1" "Retrieve version 1 detail" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/1/clauses/" "List clauses for version 1" ""
VERSION_PAYLOAD=$(jq -n --arg clause "$CLAUSE_CODE" '{
	selected_clauses: [$clause],
	change_summary: "Automation version update"
}')
run_json_test "POST" "/contracts/$CONTRACT_ID/create-version/" "Create version 2" "$VERSION_PAYLOAD" 201
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/" "List versions after addition" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/2" "Retrieve version 2 detail" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/download-url/" "Get contract download URL" ""
APPROVE_PAYLOAD=$(jq -n '{
	reviewed: true,
	comments: "Approved by automation suite"
}')
run_json_test "POST" "/contracts/$CONTRACT_ID/approve/" "Approve contract" "$APPROVE_PAYLOAD" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/download/" "Download approved contract" ""
VALIDATE_PAYLOAD=$(jq -n --arg clause "$CLAUSE_CODE" '{
	contract_type: "MSA",
	contract_value: 250000,
	selected_clauses: [$clause]
}')
run_json_test "POST" "/contracts/validate-clauses/" "Validate selected clauses" "$VALIDATE_PAYLOAD" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/history/" "Fetch contract history" ""
run_json_test "POST" "/contracts/$CONTRACT_ID/clone/" "Clone contract" '{}' 201
CLONE_CONTRACT_ID=$(echo "$LAST_BODY" | jq -r '.id')
run_json_test "GET" "/contracts/$CLONE_CONTRACT_ID/" "Retrieve cloned contract detail" ""
run_json_test "GET" "/contracts/$CLONE_CONTRACT_ID/versions/" "List cloned contract versions" ""
run_json_test "GET" "/contracts/recent/?limit=5" "Recent contracts after creation" ""
run_json_test "GET" "/contracts/statistics/" "Statistics after contract creation" ""
run_json_test "GET" "/contracts/?page=1&page_size=5" "Paginate contracts (page 1)" ""
run_json_test "GET" "/contracts/?page=2&page_size=5" "Paginate contracts (page 2)" ""
run_json_test "GET" "/contracts/?status=approved" "Filter contracts approved" ""
run_json_test "GET" "/contracts/?status=draft&contract_type=MSA" "Filter contracts by status+type" ""
run_json_test "GET" "/contracts/?search=Nonexistent" "Search contracts with no results" ""

echo -e "${BLUE}=== SECTION 5: CLAUSE ANALYTICS & VARIANTS ===${NC}"

SUGGESTIONS_PAYLOAD=$(jq -n --arg contract "$CONTRACT_ID" '{
	contract_id: $contract
}')
run_json_test "POST" "/clauses/contract-suggestions/" "Clause suggestions for contract" "$SUGGESTIONS_PAYLOAD" ""
run_json_test "POST" "/clauses/bulk-suggestions/" "Bulk suggestions for contracts" "{\"contract_ids\":[\"$CONTRACT_ID\",\"$CLONE_CONTRACT_ID\"]}" ""
DRAFT_PATCH=$(jq -n '{status: "draft"}')
run_json_test "PATCH" "/clauses/$SECOND_CLAUSE_ID/" "Move secondary clause to draft" "$DRAFT_PATCH" ""
run_json_test "GET" "/clauses/?status=draft" "List draft clauses" ""
ARCHIVE_PATCH=$(jq -n '{status: "archived"}')
run_json_test "PATCH" "/clauses/$SECOND_CLAUSE_ID/" "Archive secondary clause" "$ARCHIVE_PATCH" ""
run_json_test "GET" "/clauses/?status=archived" "List archived clauses" ""
PUBLISH_PATCH=$(jq -n '{status: "published"}')
run_json_test "PATCH" "/clauses/$SECOND_CLAUSE_ID/" "Republish secondary clause" "$PUBLISH_PATCH" ""
run_json_test "GET" "/clauses/?status=published" "List published clauses" ""
run_json_test "GET" "/clauses/?page=1&page_size=5" "Paginate clauses page 1" ""
run_json_test "GET" "/clauses/?page=2&page_size=5" "Paginate clauses page 2" ""
run_json_test "GET" "/clauses/?ordering=name" "Order clauses by name" ""
run_json_test "GET" "/clauses/?contract_type=MSA&is_mandatory=true" "Filter mandatory clauses" ""
run_json_test "GET" "/clauses/?contract_type=MSA&is_mandatory=false" "Filter optional clauses" ""
run_json_test "GET" "/clauses/?search=Automation" "Search clauses automation" ""
run_json_test "GET" "/clauses/?search=Nonexistent" "Search clauses nonexistent" ""
run_json_test "GET" "/clauses/?page_size=1" "Paginate clauses page_size=1" ""
run_json_test "GET" "/clauses/?page=1&page_size=1&search=Automation" "Paginate clause search" ""
run_json_test "GET" "/clauses/?page=1&page_size=5&status=published" "Paginate published clauses" ""
run_json_test "GET" "/clauses/?page=1&page_size=5&status=draft" "Paginate draft clauses" ""
run_json_test "GET" "/clauses/?page=1&page_size=5&status=archived" "Paginate archived clauses" ""
run_json_test "GET" "/clauses/?page=1&page_size=5&contract_type=UNKNOWN" "Paginate unknown type clauses" ""

echo -e "${BLUE}=== SECTION 6: VERSION & DOWNLOAD VALIDATIONS ===${NC}"

run_json_test "GET" "/contracts/$CONTRACT_ID/versions/1/clauses/" "Re-fetch version 1 clauses" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/versions/2/clauses/" "Fetch version 2 clauses" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/download-url/" "Re-fetch contract download URL" ""
run_json_test "GET" "/contracts/$CLONE_CONTRACT_ID/download-url/" "Clone contract download URL" ""
run_json_test "GET" "/contracts/$CONTRACT_ID/download/" "Re-download approved contract" ""

echo -e "\n${BLUE}=== TEST SUMMARY ===${NC}"
echo "Total Tests: $TEST_COUNT"
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"

if [ $TEST_COUNT -gt 0 ]; then
	success_rate=$((PASS * 100 / TEST_COUNT))
	echo -e "Success Rate: ${GREEN}${success_rate}%${NC}"
fi

# Disabled final report write due to disk space
# cat >> "$REPORT" << EOF
# 
# ---
# 
# ## SUMMARY
# 
# - **Total Tests**: $TEST_COUNT
# - **Passed**: $PASS
# - **Failed**: $FAIL
# - **Success Rate**: $((PASS * 100 / TEST_COUNT))%
# 
# ### Sections
# 1. Session & Connectivity
# 2. Clause Operations
# 3. Template Operations
# 4. Contract Operations
# 5. Clause Analytics & Variants
# 6. Version & Download Validations
# 
# Generated: \\$(date)
# EOF

# echo -e "\n${BLUE}Full report: $REPORT${NC}"

exit 0
