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
BACKEND_URL = "https://8e377b14-d41b-4b7b-943e-e8967dfb230e.preview.emergentagent.com/api"

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

    def test_finished_products_management(self):
        """Test finished products management APIs"""
        print("\n=== Testing Finished Products Management ===")
        
        # Test finished products creation
        products_data = [
            {"seal_type": "RSL", "material_type": "NBR", "inner_diameter": 25.0, "outer_diameter": 35.0, "height": 8.0, "quantity": 20, "unit_price": 15.0},
            {"seal_type": "RS", "material_type": "BUR", "inner_diameter": 30.0, "outer_diameter": 45.0, "height": 7.0, "quantity": 15, "unit_price": 20.0},
            {"seal_type": "B17", "material_type": "VT", "inner_diameter": 40.0, "outer_diameter": 55.0, "height": 10.0, "quantity": 10, "unit_price": 25.0}
        ]
        
        for product_data in products_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/finished-products", 
                                           json=product_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('seal_type') == product_data['seal_type']:
                        self.created_data.setdefault('finished_products', []).append(data)
                        self.log_test(f"Create Finished Product - {product_data['seal_type']}", True, f"Product ID: {data.get('id')}")
                    else:
                        self.log_test(f"Create Finished Product - {product_data['seal_type']}", False, f"Type mismatch: {data}")
                else:
                    self.log_test(f"Create Finished Product - {product_data['seal_type']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create Finished Product - {product_data['seal_type']}", False, f"Exception: {str(e)}")
        
        # Test get all finished products
        try:
            response = self.session.get(f"{BACKEND_URL}/finished-products")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Finished Products", True, f"Retrieved {len(data)} products")
                else:
                    self.log_test("Get All Finished Products", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Finished Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Finished Products", False, f"Exception: {str(e)}")

    def test_user_management(self):
        """Test user management APIs"""
        print("\n=== Testing User Management ===")
        
        # Test user creation
        users_data = [
            {"username": "محمد_أحمد", "password": "password123", "role": "user"},
            {"username": "فاطمة_علي", "password": "password456", "role": "user"},
            {"username": "أحمد_مدير", "password": "admin123", "role": "admin"}
        ]
        
        for user_data in users_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/users", 
                                           json=user_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('username') == user_data['username']:
                        self.created_data.setdefault('users', []).append(data)
                        self.log_test(f"Create User - {user_data['username']}", True, f"User ID: {data.get('id')}")
                    else:
                        self.log_test(f"Create User - {user_data['username']}", False, f"Username mismatch: {data}")
                else:
                    self.log_test(f"Create User - {user_data['username']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create User - {user_data['username']}", False, f"Exception: {str(e)}")
        
        # Test get all users
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Users", True, f"Retrieved {len(data)} users")
                else:
                    self.log_test("Get All Users", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Users", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Users", False, f"Exception: {str(e)}")

    def test_work_orders_management(self):
        """Test work orders management APIs"""
        print("\n=== Testing Work Orders Management ===")
        
        if not self.created_data['invoices']:
            self.log_test("Work Orders Management", False, "No invoices available for work order testing")
            return
        
        # Test work order creation from multiple invoices
        work_order_data = {
            "title": "أمر شغل تجريبي",
            "description": "أمر شغل لاختبار النظام",
            "priority": "عالي",
            "invoices": self.created_data['invoices'][:2] if len(self.created_data['invoices']) >= 2 else self.created_data['invoices'],
            "total_amount": sum(inv.get('total_amount', 0) for inv in self.created_data['invoices'][:2]),
            "total_items": sum(len(inv.get('items', [])) for inv in self.created_data['invoices'][:2])
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/work-orders/multiple", 
                                       json=work_order_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('title') == work_order_data['title']:
                    self.created_data.setdefault('work_orders', []).append(data)
                    self.log_test("Create Work Order", True, f"Work Order ID: {data.get('id')}")
                else:
                    self.log_test("Create Work Order", False, f"Title mismatch: {data}")
            else:
                self.log_test("Create Work Order", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Work Order", False, f"Exception: {str(e)}")
        
        # Test get all work orders
        try:
            response = self.session.get(f"{BACKEND_URL}/work-orders")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get All Work Orders", True, f"Retrieved {len(data)} work orders")
                else:
                    self.log_test("Get All Work Orders", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Work Orders", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get All Work Orders", False, f"Exception: {str(e)}")

    def test_individual_delete_apis(self):
        """Test individual delete APIs for all entities"""
        print("\n=== Testing Individual Delete APIs ===")
        
        # Test delete customer
        if self.created_data.get('customers'):
            customer_id = self.created_data['customers'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/customers/{customer_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف العميل بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/customers/{customer_id}")
                        if verify_response.status_code == 404:
                            self.log_test("Delete Customer", True, f"Customer {customer_id} deleted successfully from database")
                        else:
                            self.log_test("Delete Customer", False, f"Customer still exists in database after deletion")
                    else:
                        self.log_test("Delete Customer", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Customer", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Customer", False, f"Exception: {str(e)}")
        
        # Test delete finished product
        if self.created_data.get('finished_products'):
            product_id = self.created_data['finished_products'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/finished-products/{product_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف المنتج بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/finished-products")
                        if verify_response.status_code == 200:
                            products = verify_response.json()
                            if not any(p.get('id') == product_id for p in products):
                                self.log_test("Delete Finished Product", True, f"Product {product_id} deleted successfully from database")
                            else:
                                self.log_test("Delete Finished Product", False, f"Product still exists in database after deletion")
                        else:
                            self.log_test("Delete Finished Product", False, f"Failed to verify deletion")
                    else:
                        self.log_test("Delete Finished Product", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Finished Product", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Finished Product", False, f"Exception: {str(e)}")
        
        # Test delete payment
        if self.created_data.get('payments'):
            payment_id = self.created_data['payments'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/payments/{payment_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف الدفعة بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/payments")
                        if verify_response.status_code == 200:
                            payments = verify_response.json()
                            if not any(p.get('id') == payment_id for p in payments):
                                self.log_test("Delete Payment", True, f"Payment {payment_id} deleted successfully from database")
                            else:
                                self.log_test("Delete Payment", False, f"Payment still exists in database after deletion")
                        else:
                            self.log_test("Delete Payment", False, f"Failed to verify deletion")
                    else:
                        self.log_test("Delete Payment", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Payment", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Payment", False, f"Exception: {str(e)}")
        
        # Test delete work order
        if self.created_data.get('work_orders'):
            work_order_id = self.created_data['work_orders'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/work-orders/{work_order_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف أمر الشغل بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/work-orders")
                        if verify_response.status_code == 200:
                            work_orders = verify_response.json()
                            if not any(wo.get('id') == work_order_id for wo in work_orders):
                                self.log_test("Delete Work Order", True, f"Work Order {work_order_id} deleted successfully from database")
                            else:
                                self.log_test("Delete Work Order", False, f"Work Order still exists in database after deletion")
                        else:
                            self.log_test("Delete Work Order", False, f"Failed to verify deletion")
                    else:
                        self.log_test("Delete Work Order", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Work Order", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Work Order", False, f"Exception: {str(e)}")
        
        # Test delete user
        if self.created_data.get('users'):
            user_id = self.created_data['users'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/users/{user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف المستخدم بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                        if verify_response.status_code == 404:
                            self.log_test("Delete User", True, f"User {user_id} deleted successfully from database")
                        else:
                            self.log_test("Delete User", False, f"User still exists in database after deletion")
                    else:
                        self.log_test("Delete User", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete User", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete User", False, f"Exception: {str(e)}")
        
        # Test existing delete APIs
        # Test delete raw material
        if self.created_data.get('raw_materials'):
            material_id = self.created_data['raw_materials'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/raw-materials/{material_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف المادة بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/raw-materials")
                        if verify_response.status_code == 200:
                            materials = verify_response.json()
                            if not any(m.get('id') == material_id for m in materials):
                                self.log_test("Delete Raw Material", True, f"Material {material_id} deleted successfully from database")
                            else:
                                self.log_test("Delete Raw Material", False, f"Material still exists in database after deletion")
                        else:
                            self.log_test("Delete Raw Material", False, f"Failed to verify deletion")
                    else:
                        self.log_test("Delete Raw Material", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Raw Material", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Raw Material", False, f"Exception: {str(e)}")
        
        # Test delete invoice
        if self.created_data.get('invoices'):
            invoice_id = self.created_data['invoices'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/invoices/{invoice_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف الفاتورة بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/invoices/{invoice_id}")
                        if verify_response.status_code == 404:
                            self.log_test("Delete Invoice", True, f"Invoice {invoice_id} deleted successfully from database")
                        else:
                            self.log_test("Delete Invoice", False, f"Invoice still exists in database after deletion")
                    else:
                        self.log_test("Delete Invoice", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Invoice", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Invoice", False, f"Exception: {str(e)}")
        
        # Test delete expense
        if self.created_data.get('expenses'):
            expense_id = self.created_data['expenses'][0]['id']
            try:
                response = self.session.delete(f"{BACKEND_URL}/expenses/{expense_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "تم حذف المصروف بنجاح" in data.get('message', ''):
                        # Verify deletion from database
                        verify_response = self.session.get(f"{BACKEND_URL}/expenses")
                        if verify_response.status_code == 200:
                            expenses = verify_response.json()
                            if not any(e.get('id') == expense_id for e in expenses):
                                self.log_test("Delete Expense", True, f"Expense {expense_id} deleted successfully from database")
                            else:
                                self.log_test("Delete Expense", False, f"Expense still exists in database after deletion")
                        else:
                            self.log_test("Delete Expense", False, f"Failed to verify deletion")
                    else:
                        self.log_test("Delete Expense", False, f"Unexpected response message: {data}")
                else:
                    self.log_test("Delete Expense", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Delete Expense", False, f"Exception: {str(e)}")

    def test_clear_all_apis(self):
        """Test clear all APIs for all entities"""
        print("\n=== Testing Clear All APIs ===")
        
        # First, create some test data to clear
        self.test_customer_management()
        self.test_raw_materials_management()
        self.test_finished_products_management()
        self.test_invoice_management()
        self.test_expense_management()
        self.test_payment_management()
        self.test_work_orders_management()
        self.test_user_management()
        
        # Test clear all customers
        try:
            response = self.session.delete(f"{BACKEND_URL}/customers/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "عميل" in data.get('message', ''):
                    # Verify all customers are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/customers")
                    if verify_response.status_code == 200:
                        customers = verify_response.json()
                        if len(customers) == 0:
                            self.log_test("Clear All Customers", True, f"All customers cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Customers", False, f"Some customers still exist after clear all: {len(customers)}")
                    else:
                        self.log_test("Clear All Customers", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Customers", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Customers", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Customers", False, f"Exception: {str(e)}")
        
        # Test clear all raw materials
        try:
            response = self.session.delete(f"{BACKEND_URL}/raw-materials/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "مادة خام" in data.get('message', ''):
                    # Verify all raw materials are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/raw-materials")
                    if verify_response.status_code == 200:
                        materials = verify_response.json()
                        if len(materials) == 0:
                            self.log_test("Clear All Raw Materials", True, f"All raw materials cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Raw Materials", False, f"Some raw materials still exist after clear all: {len(materials)}")
                    else:
                        self.log_test("Clear All Raw Materials", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Raw Materials", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Raw Materials", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Raw Materials", False, f"Exception: {str(e)}")
        
        # Test clear all finished products
        try:
            response = self.session.delete(f"{BACKEND_URL}/finished-products/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "منتج جاهز" in data.get('message', ''):
                    # Verify all finished products are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/finished-products")
                    if verify_response.status_code == 200:
                        products = verify_response.json()
                        if len(products) == 0:
                            self.log_test("Clear All Finished Products", True, f"All finished products cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Finished Products", False, f"Some finished products still exist after clear all: {len(products)}")
                    else:
                        self.log_test("Clear All Finished Products", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Finished Products", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Finished Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Finished Products", False, f"Exception: {str(e)}")
        
        # Test clear all invoices
        try:
            response = self.session.delete(f"{BACKEND_URL}/invoices/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "فاتورة" in data.get('message', ''):
                    # Verify all invoices are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/invoices")
                    if verify_response.status_code == 200:
                        invoices = verify_response.json()
                        if len(invoices) == 0:
                            self.log_test("Clear All Invoices", True, f"All invoices cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Invoices", False, f"Some invoices still exist after clear all: {len(invoices)}")
                    else:
                        self.log_test("Clear All Invoices", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Invoices", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Invoices", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Invoices", False, f"Exception: {str(e)}")
        
        # Test clear all expenses
        try:
            response = self.session.delete(f"{BACKEND_URL}/expenses/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "مصروف" in data.get('message', ''):
                    # Verify all expenses are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/expenses")
                    if verify_response.status_code == 200:
                        expenses = verify_response.json()
                        if len(expenses) == 0:
                            self.log_test("Clear All Expenses", True, f"All expenses cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Expenses", False, f"Some expenses still exist after clear all: {len(expenses)}")
                    else:
                        self.log_test("Clear All Expenses", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Expenses", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Expenses", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Expenses", False, f"Exception: {str(e)}")
        
        # Test clear all payments
        try:
            response = self.session.delete(f"{BACKEND_URL}/payments/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "دفعة" in data.get('message', ''):
                    # Verify all payments are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/payments")
                    if verify_response.status_code == 200:
                        payments = verify_response.json()
                        if len(payments) == 0:
                            self.log_test("Clear All Payments", True, f"All payments cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Payments", False, f"Some payments still exist after clear all: {len(payments)}")
                    else:
                        self.log_test("Clear All Payments", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Payments", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Payments", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Payments", False, f"Exception: {str(e)}")
        
        # Test clear all work orders
        try:
            response = self.session.delete(f"{BACKEND_URL}/work-orders/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "أمر شغل" in data.get('message', ''):
                    # Verify all work orders are deleted from database
                    verify_response = self.session.get(f"{BACKEND_URL}/work-orders")
                    if verify_response.status_code == 200:
                        work_orders = verify_response.json()
                        if len(work_orders) == 0:
                            self.log_test("Clear All Work Orders", True, f"All work orders cleared successfully. Deleted: {data.get('deleted_count', 0)}")
                        else:
                            self.log_test("Clear All Work Orders", False, f"Some work orders still exist after clear all: {len(work_orders)}")
                    else:
                        self.log_test("Clear All Work Orders", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Work Orders", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Work Orders", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Work Orders", False, f"Exception: {str(e)}")
        
        # Test clear all users (should preserve default users)
        try:
            response = self.session.delete(f"{BACKEND_URL}/users/clear-all")
            
            if response.status_code == 200:
                data = response.json()
                if "تم حذف" in data.get('message', '') and "مستخدم" in data.get('message', ''):
                    # Verify only custom users are deleted, default users preserved
                    verify_response = self.session.get(f"{BACKEND_URL}/users")
                    if verify_response.status_code == 200:
                        users = verify_response.json()
                        # Should only have default users (if any were created in database)
                        self.log_test("Clear All Users", True, f"Custom users cleared successfully. Deleted: {data.get('deleted_count', 0)}, Remaining: {len(users)}")
                    else:
                        self.log_test("Clear All Users", False, f"Failed to verify clear all")
                else:
                    self.log_test("Clear All Users", False, f"Unexpected response message: {data}")
            else:
                self.log_test("Clear All Users", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Clear All Users", False, f"Exception: {str(e)}")

    def test_delete_error_handling(self):
        """Test error handling for delete APIs with non-existent IDs"""
        print("\n=== Testing Delete Error Handling ===")
        
        fake_id = "non-existent-id-12345"
        
        # Test delete non-existent customer
        try:
            response = self.session.delete(f"{BACKEND_URL}/customers/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "العميل غير موجود" in data.get('detail', ''):
                    self.log_test("Delete Non-existent Customer", True, "Correctly returned 404 with Arabic error message")
                else:
                    self.log_test("Delete Non-existent Customer", False, f"Wrong error message: {data}")
            else:
                self.log_test("Delete Non-existent Customer", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Non-existent Customer", False, f"Exception: {str(e)}")
        
        # Test delete non-existent finished product
        try:
            response = self.session.delete(f"{BACKEND_URL}/finished-products/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "المنتج غير موجود" in data.get('detail', ''):
                    self.log_test("Delete Non-existent Product", True, "Correctly returned 404 with Arabic error message")
                else:
                    self.log_test("Delete Non-existent Product", False, f"Wrong error message: {data}")
            else:
                self.log_test("Delete Non-existent Product", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Non-existent Product", False, f"Exception: {str(e)}")
        
        # Test delete non-existent payment
        try:
            response = self.session.delete(f"{BACKEND_URL}/payments/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "الدفعة غير موجودة" in data.get('detail', ''):
                    self.log_test("Delete Non-existent Payment", True, "Correctly returned 404 with Arabic error message")
                else:
                    self.log_test("Delete Non-existent Payment", False, f"Wrong error message: {data}")
            else:
                self.log_test("Delete Non-existent Payment", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Non-existent Payment", False, f"Exception: {str(e)}")
        
        # Test delete non-existent work order
        try:
            response = self.session.delete(f"{BACKEND_URL}/work-orders/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "أمر الشغل غير موجود" in data.get('detail', ''):
                    self.log_test("Delete Non-existent Work Order", True, "Correctly returned 404 with Arabic error message")
                else:
                    self.log_test("Delete Non-existent Work Order", False, f"Wrong error message: {data}")
            else:
                self.log_test("Delete Non-existent Work Order", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Non-existent Work Order", False, f"Exception: {str(e)}")
        
        # Test delete non-existent user
        try:
            response = self.session.delete(f"{BACKEND_URL}/users/{fake_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "المستخدم غير موجود" in data.get('detail', ''):
                    self.log_test("Delete Non-existent User", True, "Correctly returned 404 with Arabic error message")
                else:
                    self.log_test("Delete Non-existent User", False, f"Wrong error message: {data}")
            else:
                self.log_test("Delete Non-existent User", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Non-existent User", False, f"Exception: {str(e)}")
    
    def test_daily_work_order_functionality(self):
        """Test daily work order automatic functionality"""
        print("\n=== Testing Daily Work Order Functionality ===")
        
        # First, ensure we have some customers and raw materials for testing
        if not self.created_data.get('customers'):
            self.test_customer_management()
        if not self.created_data.get('raw_materials'):
            self.test_raw_materials_management()
        
        if not self.created_data.get('customers') or not self.created_data.get('raw_materials'):
            self.log_test("Daily Work Order Setup", False, "No customers or raw materials available for testing")
            return
        
        # Test 1: Create first invoice with supervisor name - should create daily work order automatically
        supervisor_name = "المهندس أحمد الصاوي"
        today = datetime.now().strftime("%Y-%m-%d")
        
        invoice_data_1 = {
            "customer_id": self.created_data['customers'][0]['id'],
            "customer_name": self.created_data['customers'][0]['name'],
            "items": [
                {
                    "seal_type": "RSL",
                    "material_type": "NBR",
                    "inner_diameter": 25.0,
                    "outer_diameter": 35.0,
                    "height": 8.0,
                    "quantity": 5,
                    "unit_price": 15.0,
                    "total_price": 75.0,
                    "material_used": self.created_data['raw_materials'][0]['unit_code']
                }
            ],
            "payment_method": "نقدي",
            "notes": "فاتورة اختبار أمر الشغل اليومي الأولى"
        }
        
        try:
            # Create invoice with supervisor name
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data_1,
                                       params={"supervisor_name": supervisor_name},
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                invoice_1 = response.json()
                self.created_data.setdefault('daily_invoices', []).append(invoice_1)
                self.log_test("Create First Invoice with Supervisor", True, 
                            f"Invoice: {invoice_1.get('invoice_number')}, Amount: {invoice_1.get('total_amount')}")
                
                # Test 2: Check if daily work order was created automatically
                try:
                    response = self.session.get(f"{BACKEND_URL}/work-orders/daily/{today}", 
                                              params={"supervisor_name": supervisor_name})
                    
                    if response.status_code == 200:
                        daily_work_order = response.json()
                        
                        # Verify daily work order properties
                        if (daily_work_order.get('is_daily') == True and 
                            daily_work_order.get('work_date') == today and
                            daily_work_order.get('supervisor_name') == supervisor_name and
                            len(daily_work_order.get('invoices', [])) == 1 and
                            daily_work_order.get('total_amount') == 75.0 and
                            daily_work_order.get('total_items') == 1):
                            
                            self.created_data.setdefault('daily_work_orders', []).append(daily_work_order)
                            self.log_test("Auto-Create Daily Work Order", True, 
                                        f"Daily work order created with 1 invoice, total: {daily_work_order.get('total_amount')}")
                        else:
                            self.log_test("Auto-Create Daily Work Order", False, 
                                        f"Daily work order properties incorrect: {daily_work_order}")
                    else:
                        self.log_test("Auto-Create Daily Work Order", False, 
                                    f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test("Auto-Create Daily Work Order", False, f"Exception: {str(e)}")
                
            else:
                self.log_test("Create First Invoice with Supervisor", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Create First Invoice with Supervisor", False, f"Exception: {str(e)}")
            return
        
        # Test 3: Create second invoice on same day - should add to existing daily work order
        invoice_data_2 = {
            "customer_id": self.created_data['customers'][0]['id'],
            "customer_name": self.created_data['customers'][0]['name'],
            "items": [
                {
                    "seal_type": "RS",
                    "material_type": "BUR",
                    "inner_diameter": 30.0,
                    "outer_diameter": 45.0,
                    "height": 7.0,
                    "quantity": 3,
                    "unit_price": 20.0,
                    "total_price": 60.0,
                    "material_used": self.created_data['raw_materials'][1]['unit_code'] if len(self.created_data['raw_materials']) > 1 else None
                }
            ],
            "payment_method": "آجل",
            "notes": "فاتورة اختبار أمر الشغل اليومي الثانية"
        }
        
        try:
            # Create second invoice with same supervisor
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data_2,
                                       params={"supervisor_name": supervisor_name},
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                invoice_2 = response.json()
                self.created_data['daily_invoices'].append(invoice_2)
                self.log_test("Create Second Invoice Same Day", True, 
                            f"Invoice: {invoice_2.get('invoice_number')}, Amount: {invoice_2.get('total_amount')}")
                
                # Test 4: Verify second invoice was added to same daily work order
                try:
                    response = self.session.get(f"{BACKEND_URL}/work-orders/daily/{today}", 
                                              params={"supervisor_name": supervisor_name})
                    
                    if response.status_code == 200:
                        updated_work_order = response.json()
                        
                        # Verify updated totals
                        expected_total_amount = 75.0 + 60.0  # First + Second invoice
                        expected_total_items = 2  # 1 item from each invoice
                        
                        if (len(updated_work_order.get('invoices', [])) == 2 and
                            updated_work_order.get('total_amount') == expected_total_amount and
                            updated_work_order.get('total_items') == expected_total_items):
                            
                            self.log_test("Add Second Invoice to Daily Work Order", True, 
                                        f"Daily work order now has 2 invoices, total: {updated_work_order.get('total_amount')}")
                        else:
                            self.log_test("Add Second Invoice to Daily Work Order", False, 
                                        f"Totals incorrect. Expected: {expected_total_amount}, {expected_total_items}. Got: {updated_work_order.get('total_amount')}, {updated_work_order.get('total_items')}")
                    else:
                        self.log_test("Add Second Invoice to Daily Work Order", False, 
                                    f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test("Add Second Invoice to Daily Work Order", False, f"Exception: {str(e)}")
                
            else:
                self.log_test("Create Second Invoice Same Day", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Second Invoice Same Day", False, f"Exception: {str(e)}")
        
        # Test 5: Test GET API for daily work order directly
        try:
            response = self.session.get(f"{BACKEND_URL}/work-orders/daily/{today}", 
                                      params={"supervisor_name": supervisor_name})
            
            if response.status_code == 200:
                work_order = response.json()
                
                # Verify all required fields are present and correct
                required_fields = ['id', 'title', 'description', 'supervisor_name', 'is_daily', 
                                 'work_date', 'invoices', 'total_amount', 'total_items', 'status']
                
                if all(field in work_order for field in required_fields):
                    self.log_test("GET Daily Work Order API", True, 
                                f"All required fields present. Invoices: {len(work_order.get('invoices', []))}")
                else:
                    missing_fields = [f for f in required_fields if f not in work_order]
                    self.log_test("GET Daily Work Order API", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("GET Daily Work Order API", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET Daily Work Order API", False, f"Exception: {str(e)}")
        
        # Test 6: Test creating daily work order for different date (should create new one)
        different_date = "2024-01-15"  # Fixed date for testing
        try:
            response = self.session.get(f"{BACKEND_URL}/work-orders/daily/{different_date}", 
                                      params={"supervisor_name": "مشرف آخر"})
            
            if response.status_code == 200:
                different_work_order = response.json()
                
                if (different_work_order.get('is_daily') == True and 
                    different_work_order.get('work_date') == different_date and
                    different_work_order.get('supervisor_name') == "مشرف آخر" and
                    len(different_work_order.get('invoices', [])) == 0):
                    
                    self.log_test("Create Daily Work Order Different Date", True, 
                                f"New daily work order created for {different_date}")
                else:
                    self.log_test("Create Daily Work Order Different Date", False, 
                                f"Properties incorrect: {different_work_order}")
            else:
                self.log_test("Create Daily Work Order Different Date", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Daily Work Order Different Date", False, f"Exception: {str(e)}")
        
        # Test 7: Verify WorkOrder model supports all new fields
        if self.created_data.get('daily_work_orders'):
            work_order = self.created_data['daily_work_orders'][0]
            new_fields = ['supervisor_name', 'is_daily', 'work_date', 'invoices', 'total_amount', 'total_items']
            
            if all(field in work_order for field in new_fields):
                self.log_test("WorkOrder Model New Fields", True, 
                            f"All new fields supported: {new_fields}")
            else:
                missing = [f for f in new_fields if f not in work_order]
                self.log_test("WorkOrder Model New Fields", False, f"Missing fields: {missing}")

    def test_material_details_functionality(self):
        """Test material_details field in InvoiceItem and work orders"""
        print("\n=== Testing Material Details Functionality (Unit Code Fix) ===")
        
        # First, ensure we have raw materials and customers for testing
        if not self.created_data.get('raw_materials'):
            self.test_raw_materials_management()
        if not self.created_data.get('customers'):
            self.test_customer_management()
        
        if not self.created_data.get('raw_materials') or not self.created_data.get('customers'):
            self.log_test("Material Details Test Setup", False, "Missing required test data (raw materials or customers)")
            return
        
        # Test 1: Create invoice with material_details from compatibility check
        print("\n--- Test 1: Invoice with material_details ---")
        
        # First, do a compatibility check to get material details
        compatibility_check = {
            "seal_type": "RSL",
            "inner_diameter": 25.0,
            "outer_diameter": 35.0,
            "height": 8.0
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/compatibility-check", 
                                       json=compatibility_check,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                compatibility_data = response.json()
                compatible_materials = compatibility_data.get('compatible_materials', [])
                
                if compatible_materials:
                    # Use the first compatible material
                    selected_material = compatible_materials[0]
                    
                    # Create invoice with material_details
                    invoice_data = {
                        "customer_id": self.created_data['customers'][0]['id'],
                        "customer_name": self.created_data['customers'][0]['name'],
                        "items": [
                            {
                                "seal_type": "RSL",
                                "material_type": selected_material['material_type'],
                                "inner_diameter": 25.0,
                                "outer_diameter": 35.0,
                                "height": 8.0,
                                "quantity": 5,
                                "unit_price": 20.0,
                                "total_price": 100.0,
                                "material_used": selected_material['unit_code'],
                                "material_details": {
                                    "unit_code": selected_material['unit_code'],
                                    "material_type": selected_material['material_type'],
                                    "inner_diameter": selected_material['inner_diameter'],
                                    "outer_diameter": selected_material['outer_diameter'],
                                    "height": selected_material['height'],
                                    "pieces_count": selected_material['pieces_count'],
                                    "cost_per_mm": selected_material['cost_per_mm'],
                                    "selected_from_compatibility": True
                                }
                            }
                        ],
                        "payment_method": "نقدي",
                        "notes": "اختبار حفظ تفاصيل الخامة من فحص التوافق"
                    }
                    
                    # Create the invoice
                    response = self.session.post(f"{BACKEND_URL}/invoices", 
                                               json=invoice_data,
                                               headers={'Content-Type': 'application/json'},
                                               params={"supervisor_name": "مشرف الاختبار"})
                    
                    if response.status_code == 200:
                        invoice_created = response.json()
                        self.created_data.setdefault('test_invoices', []).append(invoice_created)
                        
                        # Verify material_details is saved
                        if (invoice_created.get('items') and 
                            len(invoice_created['items']) > 0 and 
                            invoice_created['items'][0].get('material_details')):
                            
                            material_details = invoice_created['items'][0]['material_details']
                            if (material_details.get('unit_code') == selected_material['unit_code'] and
                                material_details.get('selected_from_compatibility') == True):
                                self.log_test("Create Invoice with material_details", True, 
                                            f"Invoice {invoice_created.get('invoice_number')} created with complete material_details")
                            else:
                                self.log_test("Create Invoice with material_details", False, 
                                            f"material_details incomplete: {material_details}")
                        else:
                            self.log_test("Create Invoice with material_details", False, 
                                        "material_details not found in created invoice")
                    else:
                        self.log_test("Create Invoice with material_details", False, 
                                    f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_test("Compatibility Check for Material Details", False, "No compatible materials found")
            else:
                self.log_test("Compatibility Check for Material Details", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Invoice with material_details", False, f"Exception: {str(e)}")
        
        # Test 2: Verify GET /api/invoices returns material_details
        print("\n--- Test 2: GET invoices with material_details ---")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            
            if response.status_code == 200:
                invoices = response.json()
                
                # Find our test invoice
                test_invoice = None
                for invoice in invoices:
                    if (invoice.get('items') and 
                        len(invoice['items']) > 0 and 
                        invoice['items'][0].get('material_details')):
                        test_invoice = invoice
                        break
                
                if test_invoice:
                    material_details = test_invoice['items'][0]['material_details']
                    if (material_details.get('unit_code') and 
                        material_details.get('selected_from_compatibility')):
                        self.log_test("GET invoices returns material_details", True, 
                                    f"material_details correctly retrieved: {material_details.get('unit_code')}")
                    else:
                        self.log_test("GET invoices returns material_details", False, 
                                    f"material_details incomplete in GET response: {material_details}")
                else:
                    self.log_test("GET invoices returns material_details", False, 
                                "No invoices with material_details found in GET response")
            else:
                self.log_test("GET invoices returns material_details", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET invoices returns material_details", False, f"Exception: {str(e)}")
        
        # Test 3: Verify daily work order contains material_details
        print("\n--- Test 3: Daily work order with material_details ---")
        
        try:
            # Get today's work orders
            response = self.session.get(f"{BACKEND_URL}/work-orders")
            
            if response.status_code == 200:
                work_orders = response.json()
                
                # Find daily work order
                daily_work_order = None
                for wo in work_orders:
                    if wo.get('is_daily') == True and wo.get('invoices'):
                        daily_work_order = wo
                        break
                
                if daily_work_order:
                    # Check if any invoice in the work order has material_details
                    found_material_details = False
                    for invoice in daily_work_order.get('invoices', []):
                        if (invoice.get('items') and 
                            len(invoice['items']) > 0 and 
                            invoice['items'][0].get('material_details')):
                            found_material_details = True
                            material_details = invoice['items'][0]['material_details']
                            
                            if material_details.get('unit_code'):
                                self.log_test("Daily work order contains material_details", True, 
                                            f"Work order contains invoice with material_details: {material_details.get('unit_code')}")
                            else:
                                self.log_test("Daily work order contains material_details", False, 
                                            f"material_details incomplete in work order: {material_details}")
                            break
                    
                    if not found_material_details:
                        self.log_test("Daily work order contains material_details", False, 
                                    "No invoices with material_details found in daily work order")
                else:
                    self.log_test("Daily work order contains material_details", False, 
                                "No daily work order found")
            else:
                self.log_test("Daily work order contains material_details", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Daily work order contains material_details", False, f"Exception: {str(e)}")
        
        # Test 4: Verify specific invoice GET returns material_details
        print("\n--- Test 4: GET specific invoice with material_details ---")
        
        if self.created_data.get('test_invoices'):
            test_invoice_id = self.created_data['test_invoices'][0]['id']
            
            try:
                response = self.session.get(f"{BACKEND_URL}/invoices/{test_invoice_id}")
                
                if response.status_code == 200:
                    invoice = response.json()
                    
                    if (invoice.get('items') and 
                        len(invoice['items']) > 0 and 
                        invoice['items'][0].get('material_details')):
                        
                        material_details = invoice['items'][0]['material_details']
                        if (material_details.get('unit_code') and 
                            material_details.get('selected_from_compatibility')):
                            self.log_test("GET specific invoice returns material_details", True, 
                                        f"Specific invoice correctly returns material_details: {material_details.get('unit_code')}")
                        else:
                            self.log_test("GET specific invoice returns material_details", False, 
                                        f"material_details incomplete: {material_details}")
                    else:
                        self.log_test("GET specific invoice returns material_details", False, 
                                    "material_details not found in specific invoice GET")
                else:
                    self.log_test("GET specific invoice returns material_details", False, 
                                f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("GET specific invoice returns material_details", False, f"Exception: {str(e)}")
        
        # Test 5: Test invoice without material_details (backward compatibility)
        print("\n--- Test 5: Invoice without material_details (backward compatibility) ---")
        
        try:
            invoice_data_no_details = {
                "customer_id": self.created_data['customers'][0]['id'],
                "customer_name": self.created_data['customers'][0]['name'],
                "items": [
                    {
                        "seal_type": "RS",
                        "material_type": "NBR",
                        "inner_diameter": 30.0,
                        "outer_diameter": 40.0,
                        "height": 7.0,
                        "quantity": 3,
                        "unit_price": 18.0,
                        "total_price": 54.0
                        # No material_details field
                    }
                ],
                "payment_method": "آجل",
                "notes": "اختبار التوافق العكسي بدون material_details"
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data_no_details,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                invoice_created = response.json()
                
                # Verify invoice is created successfully even without material_details
                if invoice_created.get('invoice_number'):
                    # Check that material_details is None or not present
                    item = invoice_created.get('items', [{}])[0]
                    material_details = item.get('material_details')
                    
                    if material_details is None:
                        self.log_test("Invoice without material_details (backward compatibility)", True, 
                                    f"Invoice {invoice_created.get('invoice_number')} created successfully without material_details")
                    else:
                        self.log_test("Invoice without material_details (backward compatibility)", True, 
                                    f"Invoice created with empty material_details: {material_details}")
                else:
                    self.log_test("Invoice without material_details (backward compatibility)", False, 
                                "Invoice creation failed")
            else:
                self.log_test("Invoice without material_details (backward compatibility)", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Invoice without material_details (backward compatibility)", False, f"Exception: {str(e)}")

    def test_treasury_yad_elsawy_account(self):
        """Test Treasury Yad Elsawy Account functionality"""
        print("\n=== Testing Treasury Yad Elsawy Account ===")
        
        # Test 1: Check if yad_elsawy account is included in treasury balances
        try:
            response = self.session.get(f"{BACKEND_URL}/treasury/balances")
            
            if response.status_code == 200:
                data = response.json()
                if 'yad_elsawy' in data:
                    self.log_test("Treasury Balances - Yad Elsawy Account", True, f"yad_elsawy account found with balance: {data['yad_elsawy']}")
                else:
                    self.log_test("Treasury Balances - Yad Elsawy Account", False, f"yad_elsawy account not found in balances: {list(data.keys())}")
            else:
                self.log_test("Treasury Balances - Yad Elsawy Account", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Treasury Balances - Yad Elsawy Account", False, f"Exception: {str(e)}")
        
        # Test 2: Create invoice with "يد الصاوي" payment method
        if self.created_data.get('customers'):
            invoice_data = {
                "customer_id": self.created_data['customers'][0]['id'],
                "customer_name": self.created_data['customers'][0]['name'],
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 25.0,
                        "outer_diameter": 35.0,
                        "height": 8.0,
                        "quantity": 5,
                        "unit_price": 20.0,
                        "total_price": 100.0
                    }
                ],
                "payment_method": "يد الصاوي",
                "notes": "فاتورة تجريبية - يد الصاوي"
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/invoices", 
                                           json=invoice_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('payment_method') == 'يد الصاوي':
                        self.created_data.setdefault('yad_elsawy_invoices', []).append(data)
                        self.log_test("Create Invoice - Yad Elsawy Payment", True, f"Invoice created: {data.get('invoice_number')}, Amount: {data.get('total_amount')}")
                        
                        # Verify balance update
                        balance_response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            yad_elsawy_balance = balance_data.get('yad_elsawy', 0)
                            if yad_elsawy_balance >= 100.0:  # Should include our invoice amount
                                self.log_test("Treasury Balance Update - Yad Elsawy", True, f"Balance updated correctly: {yad_elsawy_balance}")
                            else:
                                self.log_test("Treasury Balance Update - Yad Elsawy", False, f"Balance not updated correctly: {yad_elsawy_balance}")
                    else:
                        self.log_test("Create Invoice - Yad Elsawy Payment", False, f"Payment method mismatch: {data.get('payment_method')}")
                else:
                    self.log_test("Create Invoice - Yad Elsawy Payment", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Create Invoice - Yad Elsawy Payment", False, f"Exception: {str(e)}")
        
        # Test 3: Add manual transaction to yad_elsawy account
        transaction_data = {
            "account_id": "yad_elsawy",
            "transaction_type": "income",
            "amount": 250.0,
            "description": "إيداع يدوي في حساب يد الصاوي",
            "reference": "تجريبي"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/treasury/transactions", 
                                       json=transaction_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('account_id') == 'yad_elsawy' and data.get('transaction_type') == 'income':
                    self.log_test("Manual Transaction - Yad Elsawy Income", True, f"Transaction created: {data.get('amount')} - {data.get('description')}")
                else:
                    self.log_test("Manual Transaction - Yad Elsawy Income", False, f"Transaction data mismatch: {data}")
            else:
                self.log_test("Manual Transaction - Yad Elsawy Income", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Manual Transaction - Yad Elsawy Income", False, f"Exception: {str(e)}")
        
        # Test 4: Transfer funds from yad_elsawy to cash
        transfer_data = {
            "from_account": "yad_elsawy",
            "to_account": "cash",
            "amount": 150.0,
            "notes": "تحويل من يد الصاوي إلى النقدية"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/treasury/transfer", 
                                       json=transfer_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if "تم التحويل بنجاح" in data.get('message', ''):
                    self.log_test("Transfer from Yad Elsawy to Cash", True, f"Transfer successful: {transfer_data['amount']}")
                else:
                    self.log_test("Transfer from Yad Elsawy to Cash", False, f"Unexpected response: {data}")
            else:
                self.log_test("Transfer from Yad Elsawy to Cash", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Transfer from Yad Elsawy to Cash", False, f"Exception: {str(e)}")
        
        # Test 5: Transfer funds to yad_elsawy from cash
        transfer_data_reverse = {
            "from_account": "cash",
            "to_account": "yad_elsawy",
            "amount": 75.0,
            "notes": "تحويل من النقدية إلى يد الصاوي"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/treasury/transfer", 
                                       json=transfer_data_reverse,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if "تم التحويل بنجاح" in data.get('message', ''):
                    self.log_test("Transfer from Cash to Yad Elsawy", True, f"Transfer successful: {transfer_data_reverse['amount']}")
                else:
                    self.log_test("Transfer from Cash to Yad Elsawy", False, f"Unexpected response: {data}")
            else:
                self.log_test("Transfer from Cash to Yad Elsawy", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Transfer from Cash to Yad Elsawy", False, f"Exception: {str(e)}")
        
        # Test 6: Get current balance after all transactions
        try:
            response = self.session.get(f"{BACKEND_URL}/treasury/balances")
            
            if response.status_code == 200:
                data = response.json()
                yad_elsawy_balance = data.get('yad_elsawy', 0)
                self.log_test("Final Balance Check - Yad Elsawy", True, f"Current balance: {yad_elsawy_balance}")
                
                # Store balance for zeroing test
                self.yad_elsawy_current_balance = yad_elsawy_balance
            else:
                self.log_test("Final Balance Check - Yad Elsawy", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Final Balance Check - Yad Elsawy", False, f"Exception: {str(e)}")
        
        # Test 7: Test account zeroing functionality (expense transaction)
        if hasattr(self, 'yad_elsawy_current_balance') and self.yad_elsawy_current_balance > 0:
            zero_transaction_data = {
                "account_id": "yad_elsawy",
                "transaction_type": "expense",
                "amount": self.yad_elsawy_current_balance,
                "description": f"تصفير حساب يد الصاوي - المبلغ: {self.yad_elsawy_current_balance}",
                "reference": "تصفير حساب"
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/treasury/transactions", 
                                           json=zero_transaction_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('account_id') == 'yad_elsawy' and data.get('transaction_type') == 'expense':
                        self.log_test("Account Zeroing - Yad Elsawy", True, f"Zeroing transaction created: {data.get('amount')}")
                        
                        # Verify balance is now zero
                        balance_response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            final_balance = balance_data.get('yad_elsawy', 0)
                            if abs(final_balance) < 0.01:  # Allow for small floating point differences
                                self.log_test("Balance After Zeroing - Yad Elsawy", True, f"Balance successfully zeroed: {final_balance}")
                            else:
                                self.log_test("Balance After Zeroing - Yad Elsawy", False, f"Balance not zeroed correctly: {final_balance}")
                    else:
                        self.log_test("Account Zeroing - Yad Elsawy", False, f"Transaction data mismatch: {data}")
                else:
                    self.log_test("Account Zeroing - Yad Elsawy", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Account Zeroing - Yad Elsawy", False, f"Exception: {str(e)}")
        
        # Test 8: Get all treasury transactions to verify they're saved
        try:
            response = self.session.get(f"{BACKEND_URL}/treasury/transactions")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    yad_elsawy_transactions = [t for t in data if t.get('account_id') == 'yad_elsawy']
                    self.log_test("Get Treasury Transactions - Yad Elsawy", True, f"Found {len(yad_elsawy_transactions)} yad_elsawy transactions")
                else:
                    self.log_test("Get Treasury Transactions - Yad Elsawy", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get Treasury Transactions - Yad Elsawy", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Treasury Transactions - Yad Elsawy", False, f"Exception: {str(e)}")

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
        self.test_finished_products_management()
        self.test_user_management()
        self.test_compatibility_check()
        self.test_invoice_management()
        self.test_payment_management()
        self.test_expense_management()
        self.test_work_orders_management()
        self.test_inventory_update_logic()
        
        # Test new daily work order functionality
        print("\n" + "📋" * 20 + " DAILY WORK ORDER TESTS " + "📋" * 20)
        self.test_daily_work_order_functionality()
        
        # Test material details functionality (Unit Code Fix)
        print("\n" + "🔧" * 20 + " MATERIAL DETAILS TESTS " + "🔧" * 20)
        self.test_material_details_functionality()
        
        # Test Treasury Yad Elsawy Account functionality
        print("\n" + "💰" * 20 + " TREASURY YAD ELSAWY TESTS " + "💰" * 20)
        self.test_treasury_yad_elsawy_account()
        
        # Test delete functionality - the main focus
        print("\n" + "🗑️" * 20 + " DELETE FUNCTIONALITY TESTS " + "🗑️" * 20)
        self.test_individual_delete_apis()
        self.test_delete_error_handling()
        self.test_clear_all_apis()
        
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