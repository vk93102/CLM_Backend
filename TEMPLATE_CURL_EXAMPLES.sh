#!/bin/bash

# Template Endpoints Testing Guide
# Run this script to test all template management endpoints

BASE_URL="http://localhost:11000/api/v1"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}CONTRACT TEMPLATE ENDPOINTS TEST${NC}"
echo -e "${BLUE}=========================================${NC}\n"

# 1. Get all template types
echo -e "${YELLOW}1. GET /templates/types/ - Get All Template Types${NC}"
echo -e "Description: Retrieve all 7 available contract template types with full documentation\n"
echo "Command:"
echo "curl -X GET '$BASE_URL/templates/types/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json'"
echo ""

# 2. Get template summary
echo -e "${YELLOW}2. GET /templates/summary/ - Get Template Types Summary${NC}"
echo -e "Description: Quick summary of all template types with field counts\n"
echo "Command:"
echo "curl -X GET '$BASE_URL/templates/summary/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json'"
echo ""

# 3. Get NDA template details
echo -e "${YELLOW}3. GET /templates/types/NDA/ - Get NDA Template Details${NC}"
echo -e "Description: Retrieve detailed information about NDA template\n"
echo "Command:"
echo "curl -X GET '$BASE_URL/templates/types/NDA/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json'"
echo ""

# 4. Get MSA template details
echo -e "${YELLOW}4. GET /templates/types/MSA/ - Get MSA Template Details${NC}"
echo -e "Description: Retrieve detailed information about MSA template\n"
echo "Command:"
echo "curl -X GET '$BASE_URL/templates/types/MSA/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json'"
echo ""

# 5. Validate NDA data
echo -e "${YELLOW}5. POST /templates/validate/ - Validate Template Data${NC}"
echo -e "Description: Validate NDA data against required fields\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/validate/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"NDA\",
    \"data\": {
      \"effective_date\": \"2026-01-20\",
      \"first_party_name\": \"Acme Corporation\",
      \"first_party_address\": \"123 Business Ave, San Francisco, CA 94102\",
      \"second_party_name\": \"Tech Innovations Inc\",
      \"second_party_address\": \"456 Innovation Blvd, Palo Alto, CA 94301\",
      \"agreement_type\": \"Mutual\",
      \"governing_law\": \"California\"
    }
  }'"
echo ""

# 6. Create NDA template
echo -e "${YELLOW}6. POST /templates/create-from-type/ - Create NDA Template${NC}"
echo -e "Description: Create a new NDA contract template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"NDA\",
    \"name\": \"Standard NDA 2026\",
    \"description\": \"Our standard mutual NDA\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-20\",
      \"first_party_name\": \"Acme Corporation\",
      \"first_party_address\": \"123 Business Ave, San Francisco, CA 94102\",
      \"second_party_name\": \"Tech Innovations Inc\",
      \"second_party_address\": \"456 Innovation Blvd, Palo Alto, CA 94301\",
      \"agreement_type\": \"Mutual\",
      \"governing_law\": \"California\"
    }
  }'"
echo ""

# 7. Create MSA template
echo -e "${YELLOW}7. POST /templates/create-from-type/ - Create MSA Template${NC}"
echo -e "Description: Create a new MSA (Master Service Agreement) template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"MSA\",
    \"name\": \"Cloud Services MSA\",
    \"description\": \"Master Service Agreement for cloud services\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-20\",
      \"client_name\": \"Enterprise Solutions Ltd\",
      \"client_address\": \"789 Corporate Way, New York, NY 10001\",
      \"service_provider_name\": \"CloudTech Services Inc\",
      \"service_provider_address\": \"321 Cloud Street, Seattle, WA 98101\",
      \"service_description\": \"Cloud-based SaaS platform with 24/7 support\",
      \"monthly_fees\": 5000,
      \"payment_terms\": \"Net 30 from invoice date\",
      \"sla_uptime\": \"99.9% monthly uptime guarantee\"
    }
  }'"
echo ""

# 8. Create Employment template
echo -e "${YELLOW}8. POST /templates/create-from-type/ - Create Employment Template${NC}"
echo -e "Description: Create a new Employment Agreement template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"EMPLOYMENT\",
    \"name\": \"Senior Engineer Employment Agreement\",
    \"description\": \"Full-time employment contract for senior engineers\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-02-01\",
      \"employer_name\": \"Global Tech Corporation\",
      \"employer_address\": \"100 Tech Plaza, Austin, TX 78701\",
      \"employee_name\": \"John Smith\",
      \"employee_address\": \"456 Residential Lane, Austin, TX 78704\",
      \"job_title\": \"Senior Software Engineer\",
      \"employment_type\": \"Full-Time\",
      \"annual_salary\": 150000,
      \"start_date\": \"2026-02-15\"
    }
  }'"
echo ""

# 9. Create Service Agreement template
echo -e "${YELLOW}9. POST /templates/create-from-type/ - Create Service Agreement Template${NC}"
echo -e "Description: Create a new Service Agreement template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"SERVICE_AGREEMENT\",
    \"name\": \"Consulting Services Agreement\",
    \"description\": \"Professional consulting services agreement\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-15\",
      \"service_provider_name\": \"Consulting Partners LLC\",
      \"service_provider_address\": \"222 Consulting Drive, Boston, MA 02101\",
      \"client_name\": \"Manufacturing Company\",
      \"client_address\": \"333 Factory Road, Boston, MA 02102\",
      \"scope_of_services\": \"Business process optimization and supply chain analysis\",
      \"total_project_value\": 50000,
      \"payment_schedule\": \"25% upon signing, 25% at midpoint, 50% upon completion\"
    }
  }'"
echo ""

# 10. Create Agency Agreement template
echo -e "${YELLOW}10. POST /templates/create-from-type/ - Create Agency Agreement Template${NC}"
echo -e "Description: Create a new Agency Agreement template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"AGENCY_AGREEMENT\",
    \"name\": \"Sales Agent Agreement\",
    \"description\": \"Agreement establishing sales agent relationship\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-10\",
      \"principal_name\": \"Tech Products Inc\",
      \"principal_address\": \"100 Innovation Way, San Jose, CA 95110\",
      \"agent_name\": \"Dynamic Sales Solutions LLC\",
      \"agent_address\": \"200 Commerce Drive, San Jose, CA 95110\",
      \"scope_of_agency\": \"Exclusive sales representation for West Coast region\",
      \"compensation_structure\": \"15% commission on all sales\"
    }
  }'"
echo ""

# 11. Create Property Management template
echo -e "${YELLOW}11. POST /templates/create-from-type/ - Create Property Management Template${NC}"
echo -e "Description: Create a new Property Management Agreement template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"PROPERTY_MANAGEMENT\",
    \"name\": \"Commercial Property Management Agreement\",
    \"description\": \"Agreement for commercial real estate management\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-01\",
      \"owner_name\": \"Summit Real Estate Holdings\",
      \"owner_address\": \"300 Summit Plaza, Denver, CO 80202\",
      \"manager_name\": \"Professional Property Management Inc\",
      \"manager_address\": \"400 Professional Drive, Denver, CO 80202\",
      \"property_address\": \"500 Office Tower, Denver, CO 80202\",
      \"management_fees_percentage\": 5,
      \"services_included\": \"Tenant relations, maintenance coordination, rent collection, accounting\"
    }
  }'"
echo ""

# 12. Create Purchase Agreement template
echo -e "${YELLOW}12. POST /templates/create-from-type/ - Create Purchase Agreement Template${NC}"
echo -e "Description: Create a new Purchase Agreement template\n"
echo "Command:"
echo "curl -X POST '$BASE_URL/templates/create-from-type/' \\"
echo "  -H 'Authorization: Token YOUR_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"template_type\": \"PURCHASE_AGREEMENT\",
    \"name\": \"Equipment Purchase Agreement\",
    \"description\": \"Standard agreement for equipment purchase\",
    \"status\": \"published\",
    \"data\": {
      \"effective_date\": \"2026-01-25\",
      \"buyer_name\": \"Industrial Manufacturing Corp\",
      \"buyer_address\": \"600 Factory Lane, Cleveland, OH 44114\",
      \"seller_name\": \"Premium Equipment Company\",
      \"seller_address\": \"700 Supply Street, Cleveland, OH 44114\",
      \"item_description\": \"5x CNC Machining Centers with precision components\",
      \"purchase_price\": 500000,
      \"payment_terms\": \"50% upon signing, 50% upon delivery and acceptance\",
      \"delivery_date\": \"2026-04-30\"
    }
  }'"
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Template Management Reference Complete${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${YELLOW}To use these endpoints:${NC}"
echo "1. Replace YOUR_TOKEN with your actual authentication token"
echo "2. Copy the curl command into your terminal"
echo "3. Responses will show JSON with template details"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "✓ 7 Template Types: NDA, MSA, EMPLOYMENT, SERVICE_AGREEMENT, AGENCY_AGREEMENT, PROPERTY_MANAGEMENT, PURCHASE_AGREEMENT"
echo "✓ Full field validation and required field enforcement"
echo "✓ Support for both draft and published templates"
echo "✓ Automatic merge field population"
echo "✓ Tenant-isolated data storage"
echo "✓ Template preview and validation endpoints"
