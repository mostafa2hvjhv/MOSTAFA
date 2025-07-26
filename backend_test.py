#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Master Seal System
اختبار شامل لـ APIs النظام الخلفي لنظام ماستر سيل
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://c9965939-3094-45ff-8084-6de7d8e64a48.preview.emergentagent.com/api"

class MasterSealAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.created_data = {
            'customers': [],
            'raw_materials': [],
            'invoices': [],
            'payments': [],
            'expenses': []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_auth_system(self):
        """Test authentication endpoints"""
        print("\n=== Testing Authentication System ===")
        
        # Test valid login - Elsawy
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", 
                                       params={"username": "Elsawy", "password": "100100"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('user', {}).get('username') == 'Elsawy':
                    self.log_test("Auth - Elsawy Login", True, "Admin user authenticated successfully")
                else:
                    self.log_test("Auth - Elsawy Login", False, f"Invalid response structure: {data}")
            else:
                self.log_test("Auth - Elsawy Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Auth - Elsawy Login", False, f"Exception: {str(e)}")
        
        # Test valid login - Root
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", 
                                       params={"username": "Root", "password": "master"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('user', {}).get('username') == 'Root':
                    self.log_test("Auth - Root Login", True, "User authenticated successfully")
                else:
                    self.log_test("Auth - Root Login", False, f"Invalid response structure: {data}")
            else:
                self.log_test("Auth - Root Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Auth - Root Login", False, f"Exception: {str(e)}")
        
        # Test invalid login
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", 
                                       params={"username": "invalid", "password": "wrong"})
            
            if response.status_code == 401:
                self.log_test("Auth - Invalid Login", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Auth - Invalid Login", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Auth - Invalid Login", False, f"Exception: {str(e)}")
    
    def test_dashboard_stats(self):
        """Test dashboard statistics API"""
        print("\n=== Testing Dashboard Statistics ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_sales', 'total_expenses', 'net_profit', 'total_unpaid', 'invoice_count', 'customer_count']
                
                if all(field in data for field in required_fields):
                    self.log_test("Dashboard Stats", True, f"All required fields present: {data}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Dashboard Stats", False, f"Missing fields: {missing}")
            else:
                self.log_test("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Exception: {str(e)}")
    
    def test_customer_management(self):
        """Test customer management APIs"""
        print("\n=== Testing Customer Management ===")
        
        # Test customer creation with Arabic names
        customers_data = [
            {"name": "أحمد محمد الصاوي", "phone": "01234567890", "address": "القاهرة، مصر الجديدة"},
            {"name": "فاطمة علي حسن", "phone": "01098765432", "address": "الجيزة، الدقي"},
            {"name": "محمود عبد الرحمن", "phone": "01156789012", "address": "الإسكندرية، سموحة"},
            {"name": "نورا أحمد سالم", "phone": "01287654321", "address": "المنصورة، وسط البلد"}
        ]
        
        for customer_data in customers_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/customers", 
                                           json=customer_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('name') == customer_data['name']:
                        self.created_data['customers'].append(data)
                        self.log_test(f"Create Customer - {customer_data['name']}", True, f"Customer ID: {data.get('id')}")
                    else:
                        self.log_test(f"Create Customer - {customer_data['name']}", False, f"Name mismatch: {data}")
                else:
                    self.log_test(f"Create Customer - {customer_data['name']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Customer - {customer_data['name']}", False, f"Exception: {str(e)}")
        
        # Test get all customers
        try:
            response = self.session.get(f"{BACKEND_URL}/customers")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Customers", True, f"Retrieved {len(data)} customers")
                else:
                    self.log_test("Get All Customers", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Customers", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Customers", False, f"Exception: {str(e)}")
        
        # Test get specific customer
        if self.created_data['customers']:
            customer_id = self.created_data['customers'][0]['id']
            try:
                response = self.session.get(f"{BACKEND_URL}/customers/{customer_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('id') == customer_id:
                        self.log_test("Get Specific Customer", True, f"Retrieved customer: {data.get('name')}")
                    else:
                        self.log_test("Get Specific Customer", False, f"ID mismatch: {data}")
                else:
                    self.log_test("Get Specific Customer", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Get Specific Customer", False, f"Exception: {str(e)}")
    
    def test_raw_materials_management(self):
        """Test raw materials inventory APIs"""
        print("\n=== Testing Raw Materials Management ===")
        
        # Test raw materials creation with different types and sizes
        materials_data = [
            {"material_type": "NBR", "inner_diameter": 25.0, "outer_diameter": 35.0, "height": 100.0, "pieces_count": 50, "unit_code": "NBR-25-35-001", "cost_per_mm": 0.15},
            {"material_type": "BUR", "inner_diameter": 30.0, "outer_diameter": 45.0, "height": 80.0, "pieces_count": 30, "unit_code": "BUR-30-45-001", "cost_per_mm": 0.20},
            {"material_type": "BT", "inner_diameter": 20.0, "outer_diameter": 28.0, "height": 120.0, "pieces_count": 75, "unit_code": "BT-20-28-001", "cost_per_mm": 0.12},
            {"material_type": "VT", "inner_diameter": 40.0, "outer_diameter": 55.0, "height": 90.0, "pieces_count": 25, "unit_code": "VT-40-55-001", "cost_per_mm": 0.25},
            {"material_type": "BOOM", "inner_diameter": 15.0, "outer_diameter": 22.0, "height": 150.0, "pieces_count": 100, "unit_code": "BOOM-15-22-001", "cost_per_mm": 0.10}
        ]
        
        for material_data in materials_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/raw-materials", 
                                           json=material_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('material_type') == material_data['material_type']:
                        self.created_data['raw_materials'].append(data)
                        self.log_test(f"Create Raw Material - {material_data['material_type']}", True, f"Unit Code: {data.get('unit_code')}")
                    else:
                        self.log_test(f"Create Raw Material - {material_data['material_type']}", False, f"Type mismatch: {data}")
                else:
                    self.log_test(f"Create Raw Material - {material_data['material_type']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Raw Material - {material_data['material_type']}", False, f"Exception: {str(e)}")
        
        # Test get all raw materials
        try:
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Raw Materials", True, f"Retrieved {len(data)} materials")
                else:
                    self.log_test("Get All Raw Materials", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Raw Materials", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Raw Materials", False, f"Exception: {str(e)}")
    
    def test_compatibility_check(self):
        """Test compatibility check API"""
        print("\n=== Testing Compatibility Check ===")
        
        # Test compatibility checks for different seal types
        compatibility_tests = [
            {"seal_type": "RSL", "inner_diameter": 25.0, "outer_diameter": 35.0, "height": 8.0},
            {"seal_type": "RS", "inner_diameter": 30.0, "outer_diameter": 45.0, "height": 7.0},
            {"seal_type": "RSE", "inner_diameter": 20.0, "outer_diameter": 28.0, "height": 6.0},
            {"seal_type": "B17", "inner_diameter": 40.0, "outer_diameter": 55.0, "height": 10.0},
            {"seal_type": "B3", "inner_diameter": 15.0, "outer_diameter": 22.0, "height": 5.0}
        ]
        
        for check_data in compatibility_tests:
            try:
                response = self.session.post(f"{BACKEND_URL}/compatibility-check", 
                                           json=check_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if 'compatible_materials' in data and 'compatible_products' in data:
                        materials_count = len(data['compatible_materials'])
                        products_count = len(data['compatible_products'])
                        self.log_test(f"Compatibility Check - {check_data['seal_type']}", True, 
                                    f"Found {materials_count} materials, {products_count} products")
                    else:
                        self.log_test(f"Compatibility Check - {check_data['seal_type']}", False, f"Missing fields: {data}")
                else:
                    self.log_test(f"Compatibility Check - {check_data['seal_type']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Compatibility Check - {check_data['seal_type']}", False, f"Exception: {str(e)}")
    
    def test_invoice_management(self):
        """Test invoice management APIs"""
        print("\n=== Testing Invoice Management ===")
        
        if not self.created_data['customers']:
            self.log_test("Invoice Management", False, "No customers available for invoice testing")
            return
        
        # Test invoice creation with different payment methods
        invoice_tests = [
            {
                "customer_id": self.created_data['customers'][0]['id'],
                "customer_name": self.created_data['customers'][0]['name'],
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 25.0,
                        "outer_diameter": 35.0,
                        "height": 8.0,
                        "quantity": 10,
                        "unit_price": 15.0,
                        "total_price": 150.0,
                        "material_used": "NBR-25-35-001"
                    }
                ],
                "payment_method": "نقدي",
                "notes": "فاتورة تجريبية - دفع نقدي"
            },
            {
                "customer_id": self.created_data['customers'][1]['id'] if len(self.created_data['customers']) > 1 else self.created_data['customers'][0]['id'],
                "customer_name": self.created_data['customers'][1]['name'] if len(self.created_data['customers']) > 1 else self.created_data['customers'][0]['name'],
                "items": [
                    {
                        "seal_type": "RS",
                        "material_type": "BUR",
                        "inner_diameter": 30.0,
                        "outer_diameter": 45.0,
                        "height": 7.0,
                        "quantity": 5,
                        "unit_price": 20.0,
                        "total_price": 100.0,
                        "material_used": "BUR-30-45-001"
                    }
                ],
                "payment_method": "آجل",
                "notes": "فاتورة تجريبية - دفع آجل"
            },
            {
                "customer_id": self.created_data['customers'][0]['id'],
                "customer_name": self.created_data['customers'][0]['name'],
                "items": [
                    {
                        "seal_type": "B17",
                        "material_type": "VT",
                        "inner_diameter": 40.0,
                        "outer_diameter": 55.0,
                        "height": 10.0,
                        "quantity": 3,
                        "unit_price": 25.0,
                        "total_price": 75.0
                    }
                ],
                "payment_method": "فودافون كاش محمد الصاوي",
                "notes": "فاتورة تجريبية - فودافون كاش"
            }
        ]
        
        for i, invoice_data in enumerate(invoice_tests):
            try:
                response = self.session.post(f"{BACKEND_URL}/invoices", 
                                           json=invoice_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('invoice_number') and data.get('total_amount'):
                        self.created_data['invoices'].append(data)
                        self.log_test(f"Create Invoice {i+1} - {invoice_data['payment_method']}", True, 
                                    f"Invoice: {data.get('invoice_number')}, Amount: {data.get('total_amount')}")
                    else:
                        self.log_test(f"Create Invoice {i+1} - {invoice_data['payment_method']}", False, f"Missing fields: {data}")
                else:
                    self.log_test(f"Create Invoice {i+1} - {invoice_data['payment_method']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Invoice {i+1} - {invoice_data['payment_method']}", False, f"Exception: {str(e)}")
        
        # Test get all invoices
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Invoices", True, f"Retrieved {len(data)} invoices")
                else:
                    self.log_test("Get All Invoices", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Invoices", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Invoices", False, f"Exception: {str(e)}")
        
        # Test get specific invoice
        if self.created_data['invoices']:
            invoice_id = self.created_data['invoices'][0]['id']
            try:
                response = self.session.get(f"{BACKEND_URL}/invoices/{invoice_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('id') == invoice_id:
                        self.log_test("Get Specific Invoice", True, f"Retrieved invoice: {data.get('invoice_number')}")
                    else:
                        self.log_test("Get Specific Invoice", False, f"ID mismatch: {data}")
                else:
                    self.log_test("Get Specific Invoice", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Get Specific Invoice", False, f"Exception: {str(e)}")
    
    def test_payment_management(self):
        """Test payment tracking APIs"""
        print("\n=== Testing Payment Management ===")
        
        if not self.created_data['invoices']:
            self.log_test("Payment Management", False, "No invoices available for payment testing")
            return
        
        # Find an invoice with remaining amount for payment testing
        deferred_invoice = None
        for invoice in self.created_data['invoices']:
            if invoice.get('payment_method') == 'آجل' and invoice.get('remaining_amount', 0) > 0:
                deferred_invoice = invoice
                break
        
        if not deferred_invoice:
            self.log_test("Payment Management", False, "No deferred invoices available for payment testing")
            return
        
        # Test payment creation with different methods
        payment_tests = [
            {
                "invoice_id": deferred_invoice['id'],
                "amount": 50.0,
                "payment_method": "نقدي",
                "notes": "دفعة جزئية نقدية"
            },
            {
                "invoice_id": deferred_invoice['id'],
                "amount": 30.0,
                "payment_method": "فودافون كاش وائل محمد",
                "notes": "دفعة جزئية فودافون كاش"
            }
        ]
        
        for i, payment_data in enumerate(payment_tests):
            try:
                response = self.session.post(f"{BACKEND_URL}/payments", 
                                           json=payment_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('invoice_id') == payment_data['invoice_id']:
                        self.created_data['payments'].append(data)
                        self.log_test(f"Create Payment {i+1} - {payment_data['payment_method']}", True, 
                                    f"Amount: {data.get('amount')}, Method: {data.get('payment_method')}")
                    else:
                        self.log_test(f"Create Payment {i+1} - {payment_data['payment_method']}", False, f"Invoice ID mismatch: {data}")
                else:
                    self.log_test(f"Create Payment {i+1} - {payment_data['payment_method']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Payment {i+1} - {payment_data['payment_method']}", False, f"Exception: {str(e)}")
        
        # Test get all payments
        try:
            response = self.session.get(f"{BACKEND_URL}/payments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Payments", True, f"Retrieved {len(data)} payments")
                else:
                    self.log_test("Get All Payments", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Payments", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Payments", False, f"Exception: {str(e)}")
    
    def test_expense_management(self):
        """Test expense management APIs"""
        print("\n=== Testing Expense Management ===")
        
        # Test expense creation with different categories
        expense_tests = [
            {"description": "شراء خامات NBR", "amount": 5000.0, "category": "خامات"},
            {"description": "راتب العامل أحمد", "amount": 3000.0, "category": "رواتب"},
            {"description": "فاتورة الكهرباء", "amount": 800.0, "category": "كهرباء"},
            {"description": "صيانة المعدات", "amount": 1200.0, "category": "صيانة"},
            {"description": "مصروفات متنوعة", "amount": 500.0, "category": "أخرى"}
        ]
        
        for expense_data in expense_tests:
            try:
                response = self.session.post(f"{BACKEND_URL}/expenses", 
                                           json=expense_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('description') == expense_data['description']:
                        self.created_data['expenses'].append(data)
                        self.log_test(f"Create Expense - {expense_data['category']}", True, 
                                    f"Amount: {data.get('amount')}, Description: {data.get('description')}")
                    else:
                        self.log_test(f"Create Expense - {expense_data['category']}", False, f"Description mismatch: {data}")
                else:
                    self.log_test(f"Create Expense - {expense_data['category']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Expense - {expense_data['category']}", False, f"Exception: {str(e)}")
        
        # Test get all expenses
        try:
            response = self.session.get(f"{BACKEND_URL}/expenses")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Expenses", True, f"Retrieved {len(data)} expenses")
                else:
                    self.log_test("Get All Expenses", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Expenses", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Expenses", False, f"Exception: {str(e)}")
    
    def test_inventory_update_logic(self):
        """Test inventory update when creating invoices"""
        print("\n=== Testing Inventory Update Logic ===")
        
        if not self.created_data['raw_materials']:
            self.log_test("Inventory Update Logic", False, "No raw materials available for inventory testing")
            return
        
        # Get initial raw material state
        material_code = self.created_data['raw_materials'][0]['unit_code']
        try:
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            if response.status_code == 200:
                materials = response.json()
                initial_material = next((m for m in materials if m['unit_code'] == material_code), None)
                if initial_material:
                    initial_height = initial_material['height']
                    self.log_test("Get Initial Material State", True, f"Initial height: {initial_height}mm")
                    
                    # Create invoice that uses this material
                    if self.created_data['customers']:
                        invoice_data = {
                            "customer_id": self.created_data['customers'][0]['id'],
                            "customer_name": self.created_data['customers'][0]['name'],
                            "items": [
                                {
                                    "seal_type": "RSL",
                                    "material_type": initial_material['material_type'],
                                    "inner_diameter": initial_material['inner_diameter'],
                                    "outer_diameter": initial_material['outer_diameter'],
                                    "height": 8.0,
                                    "quantity": 2,
                                    "unit_price": 15.0,
                                    "total_price": 30.0,
                                    "material_used": material_code
                                }
                            ],
                            "payment_method": "نقدي",
                            "notes": "اختبار تحديث المخزون"
                        }
                        
                        # Create invoice
                        response = self.session.post(f"{BACKEND_URL}/invoices", 
                                                   json=invoice_data,
                                                   headers={'Content-Type': 'application/json'})
                        
                        if response.status_code == 200:
                            # Check if inventory was updated
                            response = self.session.get(f"{BACKEND_URL}/raw-materials")
                            if response.status_code == 200:
                                updated_materials = response.json()
                                updated_material = next((m for m in updated_materials if m['unit_code'] == material_code), None)
                                if updated_material:
                                    expected_height = initial_height - (8.0 + 2) * 2  # (seal_height + 2mm) * quantity
                                    actual_height = updated_material['height']
                                    
                                    if abs(actual_height - expected_height) < 0.1:  # Allow small floating point differences
                                        self.log_test("Inventory Update Logic", True, 
                                                    f"Height correctly updated: {initial_height} -> {actual_height}")
                                    else:
                                        self.log_test("Inventory Update Logic", False, 
                                                    f"Height update incorrect: expected {expected_height}, got {actual_height}")
                                else:
                                    self.log_test("Inventory Update Logic", False, "Material not found after update")
                            else:
                                self.log_test("Inventory Update Logic", False, "Failed to retrieve updated materials")
                        else:
                            self.log_test("Inventory Update Logic", False, f"Failed to create test invoice: {response.status_code}")
                    else:
                        self.log_test("Inventory Update Logic", False, "No customers available for inventory test")
                else:
                    self.log_test("Get Initial Material State", False, "Material not found")
            else:
                self.log_test("Get Initial Material State", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Inventory Update Logic", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Master Seal Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run all test suites
        self.test_auth_system()
        self.test_dashboard_stats()
        self.test_customer_management()
        self.test_raw_materials_management()
        self.test_compatibility_check()
        self.test_invoice_management()
        self.test_payment_management()
        self.test_expense_management()
        self.test_inventory_update_logic()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n📋 CREATED TEST DATA:")
        for data_type, items in self.created_data.items():
            if items:
                print(f"  - {data_type}: {len(items)} items")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = MasterSealAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)