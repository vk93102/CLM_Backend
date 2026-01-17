#!/bin/bash

################################################################################
# PRODUCTION-LEVEL SEMANTIC SEARCH ENDPOINTS TEST SUITE
# Port: 11000
# Rate Limiting: 3 calls per minute (20 seconds between calls)
################################################################################

set -o pipefail

# Configuration
BASE_URL="http://localhost:11000/api"
JWT_TOKEN="${JWT_TOKEN:-}"
RATE_LIMIT_SECONDS=20
TIMEOUT=30
VERBOSE=true
LOG_FILE="search_test_results_$(date +%Y%m%d_%H%M%S).log"

# Temp directory for responses
RESPONSE_DIR="test_responses_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESPONSE_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

################################################################################
# LOGGING & OUTPUT FUNCTIONS
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_success() {
    log "SUCCESS" "$@"
    [[ "$VERBOSE" == true ]] && echo -e "${GREEN}✓ $@${NC}"
}

log_error() {
    log "ERROR" "$@"
    [[ "$VERBOSE" == true ]] && echo -e "${RED}✗ $@${NC}"
}

log_warning() {
    log "WARNING" "$@"
    [[ "$VERBOSE" == true ]] && echo -e "${YELLOW}⚠ $@${NC}"
}

log_info() {
    log "INFO" "$@"
    [[ "$VERBOSE" == true ]] && echo -e "${BLUE}ℹ $@${NC}"
}

################################################################################
# RATE LIMITING FUNCTION
################################################################################

rate_limit() {
    local call_number=$1
    local total_calls=$2
    
    if [[ $call_number -lt $total_calls ]]; then
        log_info "Rate limiting: waiting $RATE_LIMIT_SECONDS seconds..."
        sleep "$RATE_LIMIT_SECONDS"
    fi
}

################################################################################
# PRINT RESPONSE FUNCTION
################################################################################

print_response() {
    local response="$@"
    echo -e "${CYAN}Response:${NC}"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
}

################################################################################
# AUTHENTICATION
################################################################################

get_jwt_token() {
    local email="${TEST_EMAIL:-test_search@test.com}"
    local password="${TEST_PASSWORD:-Test@1234}"
    
    # Silently get the token - don't use log functions here
    local temp_file=$(mktemp)
    local http_code=$(curl -s -o "$temp_file" -w "%{http_code}" \
        -X POST "$BASE_URL/auth/login/" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$email\", \"password\": \"$password\"}" \
        --max-time "$TIMEOUT" 2>/dev/null)
    
    local response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    if [[ $http_code -eq 200 ]]; then
        # Try to extract token using Python
        local token=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null || echo "")
        
        if [[ -n "$token" ]]; then
            # Only echo the token, nothing else
            echo "$token"
            return 0
        fi
    fi
    
    # Only echo empty on failure
    echo ""
    return 1
}

################################################################################
# VALIDATION FUNCTIONS
################################################################################

validate_response() {
    local response=$1
    local endpoint=$2
    
    if [[ -z "$response" ]]; then
        log_error "Empty response from $endpoint"
        return 1
    fi
    
    if [[ $response == *'"results"'* ]] || [[ $response == *'"count":'* ]] || [[ $response == *'"success":true'* ]]; then
        log_success "Response valid for $endpoint"
        return 0
    else
        log_error "Invalid response for $endpoint"
        return 1
    fi
}

check_http_status() {
    local status=$1
    local endpoint=$2
    
    if [[ -z "$status" ]] || [[ "$status" == "000" ]]; then
        log_error "No response from server for $endpoint (curl failed)"
        return 1
    fi
    
    if [[ $status -eq 200 ]]; then
        log_success "HTTP 200 OK for $endpoint"
        return 0
    elif [[ $status -eq 401 ]]; then
        log_error "Authentication failed (401) for $endpoint"
        return 1
    elif [[ $status -eq 400 ]]; then
        log_error "Bad request (400) for $endpoint"
        return 1
    elif [[ $status -eq 404 ]]; then
        log_error "Endpoint not found (404) for $endpoint"
        return 1
    else
        log_error "Unexpected HTTP status $status for $endpoint"
        return 1
    fi
}

################################################################################
# TEST HELPER FUNCTION
################################################################################

run_search_test() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local query=$4
    local query_params=$5
    local data_payload=$6
    local call_num=$7
    local total=$8
    
    log_info "========================================="
    log_info "TEST: $test_name"
    log_info "========================================="
    log_info "Endpoint: $endpoint"
    log_info "Query: $query"
    log_info "JWT Token length: ${#JWT_TOKEN}"
    
    local temp_file=$(mktemp)
    local http_code=""
    local response=""
    
    if [[ "$method" == "GET" ]]; then
        http_code=$(curl -s -o "$temp_file" -w "%{http_code}" \
            -X GET "$BASE_URL$endpoint$query_params" \
            -H "Authorization: Bearer $JWT_TOKEN" \
            -H "Content-Type: application/json" \
            --max-time "$TIMEOUT")
    else
        http_code=$(curl -s -o "$temp_file" -w "%{http_code}" \
            -X POST "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $JWT_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data_payload" \
            --max-time "$TIMEOUT")
    fi
    
    response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    log_info "HTTP Status: $http_code"
    
    # Display response
    if [[ -n "$response" ]]; then
        print_response "$response"
        # Save response to file
        echo "$response" > "$RESPONSE_DIR/${test_name// /_}_response.json" 2>/dev/null
    else
        log_warning "Empty response body"
    fi
    
    if check_http_status "$http_code" "$test_name"; then
        if validate_response "$response" "$test_name"; then
            # Try to extract count
            local count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', data.get('results_count', len(data.get('results', [])))))" 2>/dev/null || echo "N/A")
            log_success "$test_name returned $count results"
            rate_limit "$call_num" "$total"
            return 0
        fi
    fi
    
    rate_limit "$call_num" "$total"
    return 1
}

################################################################################
# SEARCH ENDPOINT TESTS
################################################################################

test_semantic_search() {
    local call_num=$1
    local total=$2
    
    local query="confidentiality"
    local threshold="0.2"
    local top_k="10"
    local query_params="?q=$query&threshold=$threshold&top_k=$top_k"
    
    run_search_test "Semantic Search (Balanced)" "GET" "/search/semantic/" "$query" "$query_params" "" "$call_num" "$total"
}

test_keyword_search() {
    local call_num=$1
    local total=$2
    
    local query="payment"
    local top_k="10"
    local query_params="?q=$query&top_k=$top_k"
    
    run_search_test "Keyword Search" "GET" "/search/keyword/" "$query" "$query_params" "" "$call_num" "$total"
}

test_clause_search() {
    local call_num=$1
    local total=$2
    
    local query="termination"
    local top_k="10"
    local query_params="?q=$query&top_k=$top_k"
    
    run_search_test "Clause-Based Search" "GET" "/search/clause/" "$query" "$query_params" "" "$call_num" "$total"
}

test_hybrid_search() {
    local call_num=$1
    local total=$2
    
    local query="data protection"
    local threshold="0.3"
    local top_k="10"
    local query_params="?q=$query&threshold=$threshold&top_k=$top_k"
    
    run_search_test "Hybrid Search (Semantic + Keyword)" "GET" "/search/hybrid/" "$query" "$query_params" "" "$call_num" "$total"
}

test_semantic_search_strict() {
    local call_num=$1
    local total=$2
    
    local query="confidentiality"
    local threshold="0.7"
    local top_k="5"
    local query_params="?q=$query&threshold=$threshold&top_k=$top_k"
    
    run_search_test "Semantic Search (Strict - High Threshold)" "GET" "/search/semantic/" "$query" "$query_params" "" "$call_num" "$total"
}

test_semantic_search_loose() {
    local call_num=$1
    local total=$2
    
    local query="breach"
    local threshold="0.1"
    local top_k="10"
    local query_params="?q=$query&threshold=$threshold&top_k=$top_k"
    
    run_search_test "Semantic Search (Loose - Low Threshold)" "GET" "/search/semantic/" "$query" "$query_params" "" "$call_num" "$total"
}

test_advanced_search() {
    local call_num=$1
    local total=$2
    
    local query="liability"
    local data_payload='{"query": "liability", "filters": {"document_type": "agreement"}, "top_k": 10}'
    
    run_search_test "Advanced Search with Filters" "POST" "/search/advanced/" "$query" "" "$data_payload" "$call_num" "$total"
}

################################################################################
# HEALTH CHECK
################################################################################

test_health_check() {
    local call_num=$1
    local total=$2
    
    log_info "========================================="
    log_info "TEST: API Health Check"
    log_info "========================================="
    
    local temp_file=$(mktemp)
    local http_code=$(curl -s -o "$temp_file" -w "%{http_code}" \
        -X GET "$BASE_URL/health/" \
        --max-time "$TIMEOUT")
    
    local response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    log_info "HTTP Status: $http_code"
    [[ -n "$response" ]] && print_response "$response"
    
    if check_http_status "$http_code" "health_check"; then
        log_success "API is healthy and reachable"
        rate_limit "$call_num" "$total"
        return 0
    fi
    
    rate_limit "$call_num" "$total"
    return 1
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    clear
    
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  PRODUCTION SEMANTIC SEARCH ENDPOINTS TEST SUITE           ║"
    echo "║  Port: 11000                                              ║"
    echo "║  Rate Limiting: 3 calls/min (20 seconds between)           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    log_info "Test started at $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "Log file: $LOG_FILE"
    log_info "Response directory: $RESPONSE_DIR"
    log_info "Base URL: $BASE_URL"
    
    # Check connectivity
    log_info "Checking API connectivity..."
    local temp_file=$(mktemp)
    local health_code=$(curl -s -o "$temp_file" -w "%{http_code}" "$BASE_URL/health/" 2>/dev/null)
    rm -f "$temp_file"
    
    if [[ ! "$health_code" =~ ^[0-9]{3}$ ]] || [[ $health_code -ne 200 ]]; then
        log_error "Cannot connect to $BASE_URL (Status: $health_code)"
        log_error "Please ensure the server is running on port 11000"
        exit 1
    fi
    log_success "API is reachable"
    echo ""
    
    # Get JWT Token
    if [[ -z "$JWT_TOKEN" ]]; then
        log_info "Attempting to obtain JWT token..."
        JWT_TOKEN=$(get_jwt_token)
        log_info "JWT token obtained (length: ${#JWT_TOKEN})"
        if [[ -z "$JWT_TOKEN" ]]; then
            log_error "Failed to obtain JWT token. Exiting."
            exit 1
        fi
        # Export JWT_TOKEN so it's available in subshells
        export JWT_TOKEN
    else
        log_info "Using provided JWT token"
        export JWT_TOKEN
    fi
    echo ""
    
    # Run tests
    local tests=(
        "test_health_check"
        "test_semantic_search"
        "test_keyword_search"
        "test_semantic_search_strict"
        "test_semantic_search_loose"
        "test_advanced_search"
    )
    
    local passed=0
    local failed=0
    local total=${#tests[@]}
    
    for i in "${!tests[@]}"; do
        local test_name="${tests[$i]}"
        echo ""
        
        if $test_name $(($i + 1)) "$total"; then
            ((passed++))
        else
            ((failed++))
        fi
    done
    
    # Summary
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                     TEST SUMMARY                          ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    printf "║ Total Tests: %-50s ║\n" "$total"
    printf "║ ${GREEN}Passed: %-53s${NC}║\n" "$passed"
    printf "║ ${RED}Failed: %-53s${NC}║\n" "$failed"
    printf "║ Execution Time: %-45s ║\n" "$(date '+%Y-%m-%d %H:%M:%S')"
    printf "║ Log File: %-52s ║\n" "$LOG_FILE"
    printf "║ Response Dir: %-50s ║\n" "$RESPONSE_DIR"
    echo "╚════════════════════════════════════════════════════════════╝"
    
    log_info "Test completed at $(date '+%Y-%m-%d %H:%M:%S')"
    
    if [[ $failed -eq 0 ]]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "$failed test(s) failed"
        log_info "Check $LOG_FILE for detailed information"
        log_info "Response files saved to $RESPONSE_DIR"
        exit 1
    fi
}

# Execute main function
main "$@"
