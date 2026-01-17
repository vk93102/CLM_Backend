"""
Comprehensive Admin API Testing on localhost:8000
Tests all admin endpoints to ensure they work properly
"""

import requests
import json
import time
from typing import Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
TIMEOUT = 10

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class AdminAPITester:
    def __init__(self):
        self.token = None
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def print_header(self, text):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}{Colors.RESET}\n")
    
    def print_success(self, message):
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
        self.passed += 1
    
    def print_error(self, message):
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
        self.failed += 1
    
    def print_info(self, message):
        print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")
    
    def print_json(self, data, title=""):
        if title:
            print(f"{Colors.BLUE}{title}{Colors.RESET}")
        print(json.dumps(data, indent=2))
    
    def login(self) -> bool:
        """Attempt to login with default credentials"""
        self.print_header("AUTHENTICATION")
        
        login_url = f"{BASE_URL}/auth/login/"
        
        # Try default credentials
        credentials = [
            {"email": "admin@example.com", "password": "admin123"},
            {"email": "admin@clm.local", "password": "admin123"},
            {"email": "test@example.com", "password": "test123"},
        ]
        
        for cred in credentials:
            try:
                print(f"Attempting login with {cred['email']}...")
                response = requests.post(login_url, json=cred, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'access' in data:
                        self.token = data['access']
                        self.print_success(f"Login successful with {cred['email']}")
                        return True
                    elif 'token' in data:
                        self.token = data['token']
                        self.print_success(f"Login successful with {cred['email']}")
                        return True
            except Exception as e:
                self.print_info(f"Login attempt failed: {str(e)}")
                continue
        
        self.print_error("Could not authenticate with any credentials")
        self.print_info("Proceeding with unauthenticated tests...")
        return False
    
    def make_request(self, method: str, endpoint: str, expected_status=None, data=None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
            else:
                response = requests.request(method, url, json=data, headers=headers, timeout=TIMEOUT)
            
            return {
                "status": response.status_code,
                "data": response.json() if response.text else None,
                "error": None,
                "success": response.status_code < 400
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": 0,
                "data": None,
                "error": "Connection refused - server may not be running",
                "success": False
            }
        except Exception as e:
            return {
                "status": 0,
                "data": None,
                "error": str(e),
                "success": False
            }
    
    def test_endpoint(self, name: str, method: str, endpoint: str, expected_status=200):
        """Test a single endpoint"""
        print(f"\nTesting: {method} {endpoint}")
        result = self.make_request(method, endpoint)
        
        if result["status"] == 0:
            self.print_error(f"{name} - {result['error']}")
            return False
        
        if result["status"] == expected_status:
            self.print_success(f"{name} - Status {result['status']}")
            if result["data"]:
                # Show summary of response
                if isinstance(result["data"], dict):
                    keys = list(result["data"].keys())[:3]
                    print(f"  Response keys: {', '.join(keys)}")
            return True
        else:
            self.print_error(f"{name} - Expected {expected_status}, got {result['status']}")
            if result["data"] and isinstance(result["data"], dict) and "error" in result["data"]:
                print(f"  Error: {result['data']['error']}")
            return False
    
    def test_admin_endpoints(self):
        """Test all admin endpoints"""
        self.print_header("ADMIN ENDPOINTS")
        
        endpoints = [
            ("Admin Dashboard", "GET", "/admin/dashboard/"),
            ("List Admin Users", "GET", "/admin/users/"),
            ("List Admin Roles", "GET", "/admin/roles/"),
            ("List Admin Permissions", "GET", "/admin/permissions/"),
            ("List Tenants", "GET", "/admin/tenants/"),
            ("List Audit Logs", "GET", "/admin/audit-logs/"),
            ("SLA Rules", "GET", "/admin/sla-rules/"),
            ("SLA Breaches", "GET", "/admin/sla-breaches/"),
        ]
        
        for name, method, endpoint in endpoints:
            self.test_endpoint(name, method, endpoint)
    
    def test_fast_endpoints(self):
        """Test fast endpoint functions"""
        self.print_header("FAST ENDPOINT FUNCTIONS")
        
        endpoints = [
            ("List Roles", "GET", "/roles/"),
            ("List Permissions", "GET", "/permissions/"),
            ("List Users", "GET", "/users/"),
        ]
        
        for name, method, endpoint in endpoints:
            self.test_endpoint(name, method, endpoint)
    
    def test_server_health(self):
        """Test if server is running"""
        self.print_header("SERVER HEALTH CHECK")
        
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code < 500:
                self.print_success("Django server is running on localhost:8000")
                return True
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to localhost:8000")
            print(f"\n{Colors.YELLOW}Server may not be running.{Colors.RESET}")
            print(f"{Colors.YELLOW}Start it with: python manage.py runserver{Colors.RESET}\n")
            return False
        except Exception as e:
            self.print_error(f"Server health check failed: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        
        print(f"{Colors.GREEN}Passed: {self.passed}/{total}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}/{total}{Colors.RESET}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.RESET}\n")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed. Check the output above.{Colors.RESET}\n")
            return False
    
    def run(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║         CLM Backend - Admin API Comprehensive Test Suite             ║")
        print("║              Testing on localhost:8000                               ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(Colors.RESET)
        
        # Check server health first
        if not self.test_server_health():
            return False
        
        # Try to login
        self.login()
        
        # Run tests
        self.test_admin_endpoints()
        self.test_fast_endpoints()
        
        # Print summary
        success = self.print_summary()
        
        return success


def main():
    """Main entry point"""
    tester = AdminAPITester()
    success = tester.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
