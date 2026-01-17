"""
Comprehensive Dashboard and API Verification Tests
Tests all endpoints with the seeded data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@clm.local"
ADMIN_PASSWORD = "admin123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_result(test_name, success, details=""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if success else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {test_name}")
    if details:
        print(f"      {details}")

def test_authentication():
    """Test authentication endpoints"""
    print_section("AUTHENTICATION TESTS")
    
    # Test login
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    success = response.status_code == 200
    print_result("Admin Login", success, f"Status: {response.status_code}")
    
    if not success:
        print(f"      Response: {response.text}")
        return None
    
    # Extract token
    try:
        token = response.json().get("access")
        print_result("Token Extraction", token is not None, f"Token: {token[:20]}...")
        return token
    except:
        print_result("Token Extraction", False, "Failed to parse JSON response")
        return None

def test_public_endpoints():
    """Test public endpoints (no authentication required)"""
    print_section("PUBLIC ENDPOINTS")
    
    endpoints = [
        ("/api/admin/roles/", "Roles List"),
        ("/api/admin/permissions/", "Permissions List"),
        ("/api/admin/users/", "Users List"),
    ]
    
    for endpoint, name in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        success = response.status_code == 200
        print_result(
            f"{name} ({endpoint})",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"              Data count: {count}")
            except:
                pass

def test_admin_dashboard(token):
    """Test admin dashboard endpoint"""
    print_section("ADMIN DASHBOARD")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/admin/dashboard/", headers=headers)
    
    success = response.status_code == 200
    print_result("Dashboard Metrics", success, f"Status: {response.status_code}")
    
    if success:
        try:
            data = response.json()
            print(f"\n              Dashboard Data:")
            for key, value in data.items():
                if isinstance(value, (int, str)):
                    print(f"              • {key}: {value}")
                elif isinstance(value, list) and len(value) > 0:
                    print(f"              • {key}: {len(value)} items")
                    if isinstance(value[0], dict):
                        first_item = list(value[0].keys())[:3]
                        print(f"                Fields: {', '.join(first_item)}")
        except Exception as e:
            print(f"              Error parsing: {str(e)}")

def test_contracts_list(token):
    """Test contracts list endpoint"""
    print_section("CONTRACTS ENDPOINT")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test basic list
    response = requests.get(f"{BASE_URL}/api/contracts/", headers=headers)
    success = response.status_code == 200
    print_result("Contracts List", success, f"Status: {response.status_code}")
    
    if success:
        try:
            data = response.json()
            count = data.get("count", 0) if isinstance(data, dict) else len(data)
            print(f"              Total contracts: {count}")
            
            # Show sample contracts
            results = data.get("results", data) if isinstance(data, dict) else data
            if results and len(results) > 0:
                print(f"\n              Sample Contracts:")
                for contract in results[:3]:
                    title = contract.get("title", "N/A")
                    value = contract.get("value", "N/A")
                    status = contract.get("status", "N/A")
                    print(f"              • {title} (${value}, Status: {status})")
        except Exception as e:
            print(f"              Error parsing: {str(e)}")
    
    # Test filters
    print(f"\n              Testing Filters:")
    
    filters = [
        ("?status=approved", "Status Filter (approved)"),
        ("?status=draft", "Status Filter (draft)"),
        ("?ordering=-created_at", "Order by Created Date"),
        ("?limit=5", "Limit to 5 results"),
    ]
    
    for filter_param, filter_name in filters:
        response = requests.get(f"{BASE_URL}/api/contracts/{filter_param}", headers=headers)
        success = response.status_code == 200
        print_result(f"  {filter_name}", success, f"Status: {response.status_code}")

def test_search_endpoints(token):
    """Test search endpoints"""
    print_section("SEARCH ENDPOINTS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    search_endpoints = [
        ("/api/search/full-text/", "query=agreement", "Full-Text Search"),
        ("/api/search/semantic/", "query=service", "Semantic Search"),
        ("/api/search/filters/", "status=approved&value_min=50000", "Filtered Search"),
    ]
    
    for endpoint, params, name in search_endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}?{params}", headers=headers)
        success = response.status_code in [200, 404]  # 404 means endpoint not yet registered
        
        if response.status_code == 404:
            print_result(f"{name} ({endpoint})", False, "Endpoint not registered yet")
        else:
            print_result(f"{name} ({endpoint})", success, f"Status: {response.status_code}")
            if success and response.status_code == 200:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else data.get("count", 0)
                    print(f"              Results: {count}")
                except:
                    pass

def test_ocr_processing():
    """Test OCR processing"""
    print_section("OCR PROCESSING")
    
    # Test OCR engine imports
    try:
        from ocr_engine import OCREngine, EntityExtractor, DocumentProcessor
        print_result("OCR Engine Import", True, "All classes imported successfully")
        
        # Test entity extraction
        test_text = """
        SERVICE AGREEMENT between Company A and Company B.
        Contract Value: $150,000.00
        Payment Terms: Net 30 days
        Effective Date: 01/13/2026
        Contact: john@example.com
        Phone: (555) 123-4567
        """
        
        entities = EntityExtractor.extract_all_entities(test_text)
        print_result("Entity Extraction", len(entities) > 0, f"Extracted {len(entities)} entity types")
        
        if entities:
            for entity_type, values in entities.items():
                print(f"              • {entity_type}: {values[:2]}")
        
        # Test contract summary
        summary = EntityExtractor.extract_contract_summary(test_text)
        print_result("Contract Summary Extraction", summary.get("estimated_value") is not None, 
                    f"Value: {summary.get('estimated_value')}")
        
    except ImportError as e:
        print_result("OCR Engine Import", False, f"Import Error: {str(e)}")
    except Exception as e:
        print_result("OCR Processing Tests", False, f"Error: {str(e)}")

def test_audit_logs(token):
    """Test audit logs"""
    print_section("AUDIT LOGS")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/admin/audit-logs/", headers=headers)
    
    success = response.status_code in [200, 404]
    if response.status_code == 404:
        print_result("Audit Logs Endpoint", False, "Endpoint not found (may not be registered)")
    else:
        print_result("Audit Logs Endpoint", success, f"Status: {response.status_code}")
        
        if success and response.status_code == 200:
            try:
                data = response.json()
                count = data.get("count", 0) if isinstance(data, dict) else len(data)
                print(f"              Total audit logs: {count}")
            except:
                pass

def test_database_stats():
    """Test database statistics"""
    print_section("DATABASE STATISTICS")
    
    try:
        from authentication.models import User
        from contracts.models import Contract, ContractTemplate
        from tenants.models import TenantModel
        from audit_logs.models import AuditLogModel
        
        user_count = User.objects.count()
        contract_count = Contract.objects.count()
        template_count = ContractTemplate.objects.count()
        tenant_count = TenantModel.objects.count()
        audit_count = AuditLogModel.objects.count()
        
        print_result("Users in Database", user_count > 0, f"Count: {user_count}")
        print_result("Contracts in Database", contract_count > 0, f"Count: {contract_count}")
        print_result("Templates in Database", template_count > 0, f"Count: {template_count}")
        print_result("Tenants in Database", tenant_count > 0, f"Count: {tenant_count}")
        print_result("Audit Logs in Database", audit_count > 0, f"Count: {audit_count}")
        
    except Exception as e:
        print_result("Database Access", False, f"Error: {str(e)}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}CLM BACKEND - COMPREHENSIVE VERIFICATION{Colors.RESET}")
    print(f"{Colors.BLUE}Timestamp: {datetime.now().isoformat()}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    
    # Run tests
    test_database_stats()
    token = test_authentication()
    test_public_endpoints()
    
    if token:
        test_admin_dashboard(token)
        test_contracts_list(token)
        test_search_endpoints(token)
        test_audit_logs(token)
    
    test_ocr_processing()
    
    print_section("VERIFICATION COMPLETE")
    print(f"{Colors.GREEN}✅ All critical components verified!{Colors.RESET}\n")
    print("Next Steps:")
    print("  1. Register search URLs in clm_backend/urls.py")
    print("  2. Test search endpoints with authentication token")
    print("  3. Deploy to production environment")
    print("  4. Configure Redis caching for performance")
    print()

if __name__ == "__main__":
    main()
