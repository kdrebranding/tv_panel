#!/usr/bin/env python3
"""
TV Panel Backend API Testing Suite
Tests the FastAPI backend endpoints for the TV Panel IPTV management system.
"""

import requests
import json
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

class TVPanelAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.admin_data = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_server_health(self) -> bool:
        """Test if server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, f"Server running: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("Server Health Check", False, f"Server returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, f"Cannot connect to server", str(e))
            return False
    
    def test_authentication_login(self) -> bool:
        """Test admin login functionality"""
        try:
            # Test with default admin credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.admin_data = data.get("admin", {})
                    self.log_test("Authentication Login", True, f"Login successful for user: {self.admin_data.get('username', 'admin')}")
                    return True
                else:
                    self.log_test("Authentication Login", False, "No access token in response", data)
                    return False
            else:
                self.log_test("Authentication Login", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication Login", False, "Login request failed", str(e))
            return False
    
    def test_authentication_register(self) -> bool:
        """Test admin registration functionality"""
        try:
            # Test registering a new admin
            register_data = {
                "username": f"testadmin_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=register_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Authentication Register", True, f"Registration successful: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("Authentication Register", False, f"Registration failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication Register", False, "Registration request failed", str(e))
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for authenticated requests"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_dashboard_stats(self) -> bool:
        """Test dashboard statistics endpoint"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.api_url}/dashboard/stats", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_clients", "active_clients", "expiring_soon", "expired_clients"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Dashboard Stats", True, f"Stats retrieved: {data}")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Dashboard Stats", False, f"Missing required fields: {missing_fields}", data)
                    return False
            else:
                self.log_test("Dashboard Stats", False, f"Stats request failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Dashboard Stats", False, "Stats request failed", str(e))
            return False
    
    def test_clients_crud(self) -> bool:
        """Test client CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET clients
            response = requests.get(f"{self.api_url}/clients", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Clients CRUD - GET", False, f"GET clients failed with status {response.status_code}", response.text)
                return False
            
            clients_data = response.json()
            self.log_test("Clients CRUD - GET", True, f"Retrieved {len(clients_data)} clients")
            
            # Test POST client (create)
            new_client_data = {
                "name": f"Test Client {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "subscription_period": 30,
                "login": f"testuser_{datetime.now().strftime('%H%M%S')}",
                "password": "testpass123",
                "mac": "00:11:22:33:44:55",
                "notes": "Test client created by automated testing"
            }
            
            response = requests.post(f"{self.api_url}/clients", json=new_client_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Clients CRUD - POST", False, f"POST client failed with status {response.status_code}", response.text)
                return False
            
            created_client = response.json()
            client_id = created_client.get("id")
            self.log_test("Clients CRUD - POST", True, f"Created client with ID: {client_id}")
            
            # Test GET specific client
            response = requests.get(f"{self.api_url}/clients/{client_id}", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Clients CRUD - GET by ID", False, f"GET client by ID failed with status {response.status_code}", response.text)
                return False
            
            client_details = response.json()
            self.log_test("Clients CRUD - GET by ID", True, f"Retrieved client: {client_details.get('name')}")
            
            # Test PUT client (update)
            update_data = {
                "name": f"Updated Test Client {datetime.now().strftime('%H%M%S')}",
                "notes": "Updated by automated testing"
            }
            
            response = requests.put(f"{self.api_url}/clients/{client_id}", json=update_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Clients CRUD - PUT", False, f"PUT client failed with status {response.status_code}", response.text)
                return False
            
            updated_client = response.json()
            self.log_test("Clients CRUD - PUT", True, f"Updated client name to: {updated_client.get('name')}")
            
            # Test DELETE client
            response = requests.delete(f"{self.api_url}/clients/{client_id}", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Clients CRUD - DELETE", False, f"DELETE client failed with status {response.status_code}", response.text)
                return False
            
            self.log_test("Clients CRUD - DELETE", True, "Client deleted successfully")
            
            return True
            
        except Exception as e:
            self.log_test("Clients CRUD", False, "CRUD operations failed", str(e))
            return False
    
    def test_panels_crud(self) -> bool:
        """Test panel CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET panels
            response = requests.get(f"{self.api_url}/panels", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Panels CRUD - GET", False, f"GET panels failed with status {response.status_code}", response.text)
                return False
            
            panels_data = response.json()
            self.log_test("Panels CRUD - GET", True, f"Retrieved {len(panels_data)} panels")
            
            # Test POST panel (create)
            new_panel_data = {
                "name": f"Test Panel {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": "https://test-panel.example.com",
                "description": "Test panel created by automated testing"
            }
            
            response = requests.post(f"{self.api_url}/panels", json=new_panel_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Panels CRUD - POST", False, f"POST panel failed with status {response.status_code}", response.text)
                return False
            
            created_panel = response.json()
            panel_id = created_panel.get("id")
            self.log_test("Panels CRUD - POST", True, f"Created panel with ID: {panel_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Panels CRUD", False, "Panel CRUD operations failed", str(e))
            return False
    
    def test_apps_crud(self) -> bool:
        """Test app CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET apps
            response = requests.get(f"{self.api_url}/apps", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Apps CRUD - GET", False, f"GET apps failed with status {response.status_code}", response.text)
                return False
            
            apps_data = response.json()
            self.log_test("Apps CRUD - GET", True, f"Retrieved {len(apps_data)} apps")
            
            # Test POST app (create)
            new_app_data = {
                "name": f"Test App {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test app created by automated testing"
            }
            
            response = requests.post(f"{self.api_url}/apps", json=new_app_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Apps CRUD - POST", False, f"POST app failed with status {response.status_code}", response.text)
                return False
            
            created_app = response.json()
            app_id = created_app.get("id")
            self.log_test("Apps CRUD - POST", True, f"Created app with ID: {app_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Apps CRUD", False, "App CRUD operations failed", str(e))
            return False
    
    def test_contact_types_crud(self) -> bool:
        """Test contact type CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET contact types
            response = requests.get(f"{self.api_url}/contact-types", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Contact Types CRUD - GET", False, f"GET contact types failed with status {response.status_code}", response.text)
                return False
            
            contact_types_data = response.json()
            self.log_test("Contact Types CRUD - GET", True, f"Retrieved {len(contact_types_data)} contact types")
            
            # Test POST contact type (create)
            new_contact_type_data = {
                "name": f"Test Contact {datetime.now().strftime('%H%M%S')}",
                "url_pattern": "https://test.com/{contact}",
                "icon": "test-icon"
            }
            
            response = requests.post(f"{self.api_url}/contact-types", json=new_contact_type_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Contact Types CRUD - POST", False, f"POST contact type failed with status {response.status_code}", response.text)
                return False
            
            created_contact_type = response.json()
            contact_type_id = created_contact_type.get("id")
            self.log_test("Contact Types CRUD - POST", True, f"Created contact type with ID: {contact_type_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Contact Types CRUD", False, "Contact type CRUD operations failed", str(e))
            return False
    
    def test_password_generator(self) -> bool:
        """Test password generator endpoint"""
        try:
            response = requests.get(f"{self.api_url}/generate-password?length=12", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                password = data.get("password", "")
                if len(password) == 12:
                    self.log_test("Password Generator", True, f"Generated password of correct length: {len(password)} chars")
                    return True
                else:
                    self.log_test("Password Generator", False, f"Password length incorrect: expected 12, got {len(password)}")
                    return False
            else:
                self.log_test("Password Generator", False, f"Password generation failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Password Generator", False, "Password generation request failed", str(e))
            return False
    
    def test_payment_methods_crud(self) -> bool:
        """Test payment methods CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET payment methods
            response = requests.get(f"{self.api_url}/payment-methods", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Payment Methods CRUD - GET", False, f"GET payment methods failed with status {response.status_code}", response.text)
                return False
            
            payment_methods_data = response.json()
            self.log_test("Payment Methods CRUD - GET", True, f"Retrieved {len(payment_methods_data)} payment methods")
            
            # Test POST payment method (create)
            new_payment_method_data = {
                "method_id": f"test_method_{datetime.now().strftime('%H%M%S')}",
                "name": f"Test Payment Method {datetime.now().strftime('%H%M%S')}",
                "description": "Test payment method created by automated testing",
                "is_active": True,
                "fee_percentage": 2.5,
                "min_amount": 10.0,
                "instructions": "Test payment instructions"
            }
            
            response = requests.post(f"{self.api_url}/payment-methods", json=new_payment_method_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Payment Methods CRUD - POST", False, f"POST payment method failed with status {response.status_code}", response.text)
                return False
            
            created_payment_method = response.json()
            payment_method_id = created_payment_method.get("id")
            self.log_test("Payment Methods CRUD - POST", True, f"Created payment method with ID: {payment_method_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Payment Methods CRUD", False, "Payment method CRUD operations failed", str(e))
            return False
    
    def test_pricing_config_crud(self) -> bool:
        """Test pricing config CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET pricing config
            response = requests.get(f"{self.api_url}/pricing-config", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Pricing Config CRUD - GET", False, f"GET pricing config failed with status {response.status_code}", response.text)
                return False
            
            pricing_config_data = response.json()
            self.log_test("Pricing Config CRUD - GET", True, f"Retrieved {len(pricing_config_data)} pricing configs")
            
            # Test POST pricing config (create)
            new_pricing_data = {
                "service_type": f"test_service_{datetime.now().strftime('%H%M%S')}",
                "price": 29.99,
                "currency": "PLN",
                "duration_days": 30,
                "is_active": True,
                "discount_percentage": 10.0,
                "description": "Test pricing config created by automated testing"
            }
            
            response = requests.post(f"{self.api_url}/pricing-config", json=new_pricing_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Pricing Config CRUD - POST", False, f"POST pricing config failed with status {response.status_code}", response.text)
                return False
            
            created_pricing = response.json()
            pricing_id = created_pricing.get("id")
            self.log_test("Pricing Config CRUD - POST", True, f"Created pricing config with ID: {pricing_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Pricing Config CRUD", False, "Pricing config CRUD operations failed", str(e))
            return False
    
    def test_questions_crud(self) -> bool:
        """Test questions/FAQ CRUD operations"""
        try:
            headers = self.get_auth_headers()
            
            # Test GET questions
            response = requests.get(f"{self.api_url}/questions", headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Questions CRUD - GET", False, f"GET questions failed with status {response.status_code}", response.text)
                return False
            
            questions_data = response.json()
            self.log_test("Questions CRUD - GET", True, f"Retrieved {len(questions_data)} questions")
            
            # Test POST question (create)
            new_question_data = {
                "question": f"Test Question {datetime.now().strftime('%H%M%S')}?",
                "answer": "This is a test answer created by automated testing.",
                "category": "Testing",
                "is_active": True
            }
            
            response = requests.post(f"{self.api_url}/questions", json=new_question_data, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Questions CRUD - POST", False, f"POST question failed with status {response.status_code}", response.text)
                return False
            
            created_question = response.json()
            question_id = created_question.get("id")
            self.log_test("Questions CRUD - POST", True, f"Created question with ID: {question_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Questions CRUD", False, "Questions CRUD operations failed", str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print("🚀 Starting TV Panel Backend API Tests")
        print(f"📡 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Test server health first
        if not self.test_server_health():
            print("❌ Server health check failed. Stopping tests.")
            return self.get_test_summary()
        
        # Test authentication
        if not self.test_authentication_login():
            print("❌ Authentication failed. Cannot proceed with authenticated tests.")
            return self.get_test_summary()
        
        # Run all other tests
        test_methods = [
            self.test_authentication_register,
            self.test_dashboard_stats,
            self.test_clients_crud,
            self.test_panels_crud,
            self.test_apps_crud,
            self.test_contact_types_crud,
            self.test_payment_methods_crud,
            self.test_pricing_config_crud,
            self.test_questions_crud,
            self.test_password_generator
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, "Test method failed", str(e))
        
        return self.get_test_summary()
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        return summary

def main():
    """Main test execution"""
    # Get backend URL from environment or use default
    import os
    
    # Try to read from frontend .env file
    frontend_env_path = "/app/frontend/.env"
    backend_url = None
    
    try:
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
    except:
        pass
    
    # Use the external URL from frontend .env for testing
    if not backend_url:
        backend_url = "http://localhost:8001"
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    # Initialize tester and run tests
    tester = TVPanelAPITester(backend_url)
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary["failed"] > 0:
        print(f"\n❌ Tests completed with {summary['failed']} failures")
        sys.exit(1)
    else:
        print(f"\n✅ All {summary['passed']} tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()