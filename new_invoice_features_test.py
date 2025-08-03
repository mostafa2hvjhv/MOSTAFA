#!/usr/bin/env python3
"""
Comprehensive Testing for New Invoice Features
اختبار شامل لميزات الفواتير الجديدة

Testing Focus:
1. Create invoices with invoice titles and supervisor names
2. Test manufactured products (existing functionality still works)
3. Test local products (new feature) - create invoices with local products that have supplier, purchase price, and selling price
4. Verify that both types of products are saved correctly with all the new fields
5. Test invoice retrieval to make sure the new fields are returned properly
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://7194fb5a-e781-47eb-a7a7-f1f4c1a30a57.preview.emergentagent.com/api"

class NewInvoiceFeaturesTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_data = {
            'customers': [],
            'raw_materials': [],
            'invoices': [],
            'work_orders': []
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
    
    def setup_test_data(self):
        """Create test customers and raw materials for invoice testing"""
        print("\n=== Setting Up Test Data ===")
        
        # Create test customers
        customers_data = [
            {"name": "شركة الأهرام للتجارة", "phone": "01234567890", "address": "القاهرة، مدينة نصر"},
            {"name": "مؤسسة النيل للصناعات", "phone": "01098765432", "address": "الجيزة، الهرم"},
            {"name": "شركة الدلتا للمعدات", "phone": "01156789012", "address": "الإسكندرية، العجمي"}
        ]
        
        for customer_data in customers_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/customers", 
                                           json=customer_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    self.created_data['customers'].append(data)
                    self.log_test(f"Setup Customer - {customer_data['name']}", True, f"Customer ID: {data.get('id')}")
                else:
                    self.log_test(f"Setup Customer - {customer_data['name']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Setup Customer - {customer_data['name']}", False, f"Exception: {str(e)}")
        
        # Create test raw materials
        materials_data = [
            {"material_type": "NBR", "inner_diameter": 25.0, "outer_diameter": 35.0, "height": 100.0, "pieces_count": 50, "unit_code": "NBR-25-35-TEST", "cost_per_mm": 0.15},
            {"material_type": "BUR", "inner_diameter": 30.0, "outer_diameter": 45.0, "height": 80.0, "pieces_count": 30, "unit_code": "BUR-30-45-TEST", "cost_per_mm": 0.20},
            {"material_type": "VT", "inner_diameter": 40.0, "outer_diameter": 55.0, "height": 90.0, "pieces_count": 25, "unit_code": "VT-40-55-TEST", "cost_per_mm": 0.25}
        ]
        
        for material_data in materials_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/raw-materials", 
                                           json=material_data,
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    data = response.json()
                    self.created_data['raw_materials'].append(data)
                    self.log_test(f"Setup Raw Material - {material_data['material_type']}", True, f"Unit Code: {data.get('unit_code')}")
                else:
                    self.log_test(f"Setup Raw Material - {material_data['material_type']}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Setup Raw Material - {material_data['material_type']}", False, f"Exception: {str(e)}")
    
    def test_invoice_with_manufactured_products_only(self):
        """Test creating invoice with manufactured products only (existing functionality)"""
        print("\n=== Testing Invoice with Manufactured Products Only ===")
        
        if not self.created_data['customers']:
            self.log_test("Invoice with Manufactured Products", False, "No customers available")
            return
        
        invoice_data = {
            "customer_id": self.created_data['customers'][0]['id'],
            "customer_name": self.created_data['customers'][0]['name'],
            "invoice_title": "فاتورة منتجات مصنعة - اختبار",
            "supervisor_name": "المهندس أحمد محمد",
            "items": [
                {
                    "product_type": "manufactured",
                    "seal_type": "RSL",
                    "material_type": "NBR",
                    "inner_diameter": 25.0,
                    "outer_diameter": 35.0,
                    "height": 8.0,
                    "quantity": 10,
                    "unit_price": 15.0,
                    "total_price": 150.0,
                    "material_used": "NBR-25-35-TEST"
                },
                {
                    "product_type": "manufactured",
                    "seal_type": "RS",
                    "material_type": "BUR",
                    "inner_diameter": 30.0,
                    "outer_diameter": 45.0,
                    "height": 7.0,
                    "quantity": 5,
                    "unit_price": 20.0,
                    "total_price": 100.0,
                    "material_used": "BUR-30-45-TEST"
                }
            ],
            "payment_method": "نقدي",
            "discount_type": "amount",
            "discount_value": 25.0,
            "notes": "فاتورة اختبار للمنتجات المصنعة مع عنوان واسم مشرف"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify all new fields are present and correct
                success_conditions = [
                    data.get('invoice_title') == invoice_data['invoice_title'],
                    data.get('supervisor_name') == invoice_data['supervisor_name'],
                    data.get('subtotal') == 250.0,  # 150 + 100
                    data.get('discount') == 25.0,
                    data.get('total_after_discount') == 225.0,  # 250 - 25
                    data.get('total_amount') == 225.0,
                    len(data.get('items', [])) == 2,
                    all(item.get('product_type') == 'manufactured' for item in data.get('items', [])),
                    data.get('items', [{}])[0].get('material_used') == 'NBR-25-35-TEST'
                ]
                
                if all(success_conditions):
                    self.created_data['invoices'].append(data)
                    self.log_test("Invoice with Manufactured Products", True, 
                                f"Invoice: {data.get('invoice_number')}, Title: {data.get('invoice_title')}, Supervisor: {data.get('supervisor_name')}, Total: {data.get('total_amount')}")
                else:
                    failed_conditions = []
                    if not success_conditions[0]: failed_conditions.append("invoice_title")
                    if not success_conditions[1]: failed_conditions.append("supervisor_name")
                    if not success_conditions[2]: failed_conditions.append("subtotal")
                    if not success_conditions[3]: failed_conditions.append("discount")
                    if not success_conditions[4]: failed_conditions.append("total_after_discount")
                    if not success_conditions[5]: failed_conditions.append("total_amount")
                    if not success_conditions[6]: failed_conditions.append("items_count")
                    if not success_conditions[7]: failed_conditions.append("product_type")
                    if not success_conditions[8]: failed_conditions.append("material_used")
                    
                    self.log_test("Invoice with Manufactured Products", False, f"Failed conditions: {failed_conditions}, Data: {data}")
            else:
                self.log_test("Invoice with Manufactured Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Invoice with Manufactured Products", False, f"Exception: {str(e)}")
    
    def test_invoice_with_local_products_only(self):
        """Test creating invoice with local products only (new feature)"""
        print("\n=== Testing Invoice with Local Products Only ===")
        
        if not self.created_data['customers']:
            self.log_test("Invoice with Local Products", False, "No customers available")
            return
        
        invoice_data = {
            "customer_id": self.created_data['customers'][1]['id'] if len(self.created_data['customers']) > 1 else self.created_data['customers'][0]['id'],
            "customer_name": self.created_data['customers'][1]['name'] if len(self.created_data['customers']) > 1 else self.created_data['customers'][0]['name'],
            "invoice_title": "فاتورة منتجات محلية - اختبار",
            "supervisor_name": "المهندس محمد علي",
            "items": [
                {
                    "product_type": "local",
                    "product_name": "حلقات مطاطية مستوردة - مقاس 25x35",
                    "supplier": "شركة المطاط المصرية",
                    "purchase_price": 8.0,
                    "selling_price": 12.0,
                    "quantity": 20,
                    "unit_price": 12.0,
                    "total_price": 240.0,
                    "local_product_details": {
                        "origin": "مصر",
                        "quality_grade": "A+",
                        "warranty_months": 12
                    }
                },
                {
                    "product_type": "local",
                    "product_name": "جوانات سيليكون - مقاس 30x45",
                    "supplier": "مؤسسة الجودة للمطاط",
                    "purchase_price": 15.0,
                    "selling_price": 22.0,
                    "quantity": 8,
                    "unit_price": 22.0,
                    "total_price": 176.0,
                    "local_product_details": {
                        "origin": "تركيا",
                        "quality_grade": "Premium",
                        "warranty_months": 24
                    }
                }
            ],
            "payment_method": "آجل",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "notes": "فاتورة اختبار للمنتجات المحلية مع تفاصيل الموردين"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify all new fields are present and correct
                subtotal = 240.0 + 176.0  # 416.0
                discount = subtotal * 0.10  # 41.6
                total_after_discount = subtotal - discount  # 374.4
                
                success_conditions = [
                    data.get('invoice_title') == invoice_data['invoice_title'],
                    data.get('supervisor_name') == invoice_data['supervisor_name'],
                    abs(data.get('subtotal', 0) - subtotal) < 0.1,
                    abs(data.get('discount', 0) - discount) < 0.1,
                    abs(data.get('total_after_discount', 0) - total_after_discount) < 0.1,
                    abs(data.get('total_amount', 0) - total_after_discount) < 0.1,
                    len(data.get('items', [])) == 2,
                    all(item.get('product_type') == 'local' for item in data.get('items', [])),
                    data.get('items', [{}])[0].get('supplier') == 'شركة المطاط المصرية',
                    data.get('items', [{}])[0].get('purchase_price') == 8.0,
                    data.get('items', [{}])[0].get('selling_price') == 12.0,
                    data.get('items', [{}])[1].get('supplier') == 'مؤسسة الجودة للمطاط',
                    data.get('remaining_amount', 0) > 0  # Should be > 0 for deferred payment
                ]
                
                if all(success_conditions):
                    self.created_data['invoices'].append(data)
                    self.log_test("Invoice with Local Products", True, 
                                f"Invoice: {data.get('invoice_number')}, Title: {data.get('invoice_title')}, Supervisor: {data.get('supervisor_name')}, Total: {data.get('total_amount')}, Remaining: {data.get('remaining_amount')}")
                else:
                    failed_conditions = []
                    condition_names = ["invoice_title", "supervisor_name", "subtotal", "discount", "total_after_discount", "total_amount", "items_count", "product_type", "supplier1", "purchase_price1", "selling_price1", "supplier2", "remaining_amount"]
                    for i, condition in enumerate(success_conditions):
                        if not condition:
                            failed_conditions.append(condition_names[i])
                    
                    self.log_test("Invoice with Local Products", False, f"Failed conditions: {failed_conditions}, Data: {data}")
            else:
                self.log_test("Invoice with Local Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Invoice with Local Products", False, f"Exception: {str(e)}")
    
    def test_invoice_with_mixed_products(self):
        """Test creating invoice with both manufactured and local products"""
        print("\n=== Testing Invoice with Mixed Products ===")
        
        if not self.created_data['customers']:
            self.log_test("Invoice with Mixed Products", False, "No customers available")
            return
        
        invoice_data = {
            "customer_id": self.created_data['customers'][2]['id'] if len(self.created_data['customers']) > 2 else self.created_data['customers'][0]['id'],
            "customer_name": self.created_data['customers'][2]['name'] if len(self.created_data['customers']) > 2 else self.created_data['customers'][0]['name'],
            "invoice_title": "فاتورة مختلطة - منتجات مصنعة ومحلية",
            "supervisor_name": "المهندس خالد حسن",
            "items": [
                # Manufactured product
                {
                    "product_type": "manufactured",
                    "seal_type": "B17",
                    "material_type": "VT",
                    "inner_diameter": 40.0,
                    "outer_diameter": 55.0,
                    "height": 10.0,
                    "quantity": 6,
                    "unit_price": 25.0,
                    "total_price": 150.0,
                    "material_used": "VT-40-55-TEST"
                },
                # Local product
                {
                    "product_type": "local",
                    "product_name": "أويل سيل مستورد - مقاس خاص",
                    "supplier": "شركة الاستيراد المتخصصة",
                    "purchase_price": 18.0,
                    "selling_price": 28.0,
                    "quantity": 4,
                    "unit_price": 28.0,
                    "total_price": 112.0,
                    "local_product_details": {
                        "origin": "ألمانيا",
                        "quality_grade": "Industrial",
                        "warranty_months": 36
                    }
                },
                # Another manufactured product
                {
                    "product_type": "manufactured",
                    "seal_type": "RSE",
                    "material_type": "NBR",
                    "inner_diameter": 25.0,
                    "outer_diameter": 35.0,
                    "height": 6.0,
                    "quantity": 12,
                    "unit_price": 14.0,
                    "total_price": 168.0,
                    "material_used": "NBR-25-35-TEST"
                }
            ],
            "payment_method": "فودافون كاش محمد الصاوي",
            "discount_type": "amount",
            "discount_value": 50.0,
            "notes": "فاتورة اختبار مختلطة - منتجات مصنعة ومحلية معاً"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", 
                                       json=invoice_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify all new fields are present and correct
                subtotal = 150.0 + 112.0 + 168.0  # 430.0
                discount = 50.0
                total_after_discount = subtotal - discount  # 380.0
                
                success_conditions = [
                    data.get('invoice_title') == invoice_data['invoice_title'],
                    data.get('supervisor_name') == invoice_data['supervisor_name'],
                    abs(data.get('subtotal', 0) - subtotal) < 0.1,
                    abs(data.get('discount', 0) - discount) < 0.1,
                    abs(data.get('total_after_discount', 0) - total_after_discount) < 0.1,
                    abs(data.get('total_amount', 0) - total_after_discount) < 0.1,
                    len(data.get('items', [])) == 3,
                    # Check product types
                    data.get('items', [{}])[0].get('product_type') == 'manufactured',
                    data.get('items', [{}])[1].get('product_type') == 'local',
                    data.get('items', [{}])[2].get('product_type') == 'manufactured',
                    # Check manufactured product fields
                    data.get('items', [{}])[0].get('seal_type') == 'B17',
                    data.get('items', [{}])[0].get('material_used') == 'VT-40-55-TEST',
                    # Check local product fields
                    data.get('items', [{}])[1].get('supplier') == 'شركة الاستيراد المتخصصة',
                    data.get('items', [{}])[1].get('purchase_price') == 18.0,
                    data.get('items', [{}])[1].get('selling_price') == 28.0,
                    # Check payment method
                    data.get('payment_method') == 'فودافون كاش محمد الصاوي',
                    data.get('remaining_amount', 0) == 0  # Should be 0 for non-deferred payment
                ]
                
                if all(success_conditions):
                    self.created_data['invoices'].append(data)
                    self.log_test("Invoice with Mixed Products", True, 
                                f"Invoice: {data.get('invoice_number')}, Title: {data.get('invoice_title')}, Supervisor: {data.get('supervisor_name')}, Total: {data.get('total_amount')}, Items: {len(data.get('items', []))}")
                else:
                    failed_conditions = []
                    condition_names = ["invoice_title", "supervisor_name", "subtotal", "discount", "total_after_discount", "total_amount", "items_count", "product_type1", "product_type2", "product_type3", "seal_type", "material_used", "supplier", "purchase_price", "selling_price", "payment_method", "remaining_amount"]
                    for i, condition in enumerate(success_conditions):
                        if not condition:
                            failed_conditions.append(condition_names[i])
                    
                    self.log_test("Invoice with Mixed Products", False, f"Failed conditions: {failed_conditions}, Data: {data}")
            else:
                self.log_test("Invoice with Mixed Products", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Invoice with Mixed Products", False, f"Exception: {str(e)}")
    
    def test_invoice_retrieval_with_new_fields(self):
        """Test invoice retrieval to ensure all new fields are returned properly"""
        print("\n=== Testing Invoice Retrieval with New Fields ===")
        
        if not self.created_data['invoices']:
            self.log_test("Invoice Retrieval", False, "No invoices available for retrieval testing")
            return
        
        # Test GET all invoices
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= len(self.created_data['invoices']):
                    # Find our test invoices
                    test_invoice_numbers = [inv.get('invoice_number') for inv in self.created_data['invoices']]
                    retrieved_invoices = [inv for inv in data if inv.get('invoice_number') in test_invoice_numbers]
                    
                    if len(retrieved_invoices) == len(self.created_data['invoices']):
                        # Verify all new fields are present in retrieved invoices
                        all_fields_present = True
                        missing_fields = []
                        
                        required_fields = ['invoice_title', 'supervisor_name', 'subtotal', 'discount', 'discount_type', 'discount_value', 'total_after_discount']
                        
                        for invoice in retrieved_invoices:
                            for field in required_fields:
                                if field not in invoice:
                                    all_fields_present = False
                                    missing_fields.append(f"{invoice.get('invoice_number', 'Unknown')}.{field}")
                            
                            # Check items have correct product_type and related fields
                            for item in invoice.get('items', []):
                                if item.get('product_type') == 'local':
                                    local_fields = ['supplier', 'purchase_price', 'selling_price']
                                    for field in local_fields:
                                        if field not in item:
                                            all_fields_present = False
                                            missing_fields.append(f"{invoice.get('invoice_number', 'Unknown')}.item.{field}")
                                elif item.get('product_type') == 'manufactured':
                                    manufactured_fields = ['seal_type', 'material_type']
                                    for field in manufactured_fields:
                                        if field not in item:
                                            all_fields_present = False
                                            missing_fields.append(f"{invoice.get('invoice_number', 'Unknown')}.item.{field}")
                        
                        if all_fields_present:
                            self.log_test("GET All Invoices - New Fields", True, 
                                        f"Retrieved {len(retrieved_invoices)} test invoices with all new fields present")
                        else:
                            self.log_test("GET All Invoices - New Fields", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("GET All Invoices - New Fields", False, 
                                    f"Expected {len(self.created_data['invoices'])} test invoices, found {len(retrieved_invoices)}")
                else:
                    self.log_test("GET All Invoices - New Fields", False, f"Expected list with at least {len(self.created_data['invoices'])} invoices, got: {len(data) if isinstance(data, list) else type(data)}")
            else:
                self.log_test("GET All Invoices - New Fields", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET All Invoices - New Fields", False, f"Exception: {str(e)}")
        
        # Test GET specific invoice
        if self.created_data['invoices']:
            test_invoice = self.created_data['invoices'][0]
            invoice_id = test_invoice['id']
            
            try:
                response = self.session.get(f"{BACKEND_URL}/invoices/{invoice_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify all new fields are present and match original data
                    success_conditions = [
                        data.get('id') == invoice_id,
                        data.get('invoice_title') == test_invoice.get('invoice_title'),
                        data.get('supervisor_name') == test_invoice.get('supervisor_name'),
                        'subtotal' in data,
                        'discount' in data,
                        'discount_type' in data,
                        'discount_value' in data,
                        'total_after_discount' in data,
                        len(data.get('items', [])) == len(test_invoice.get('items', []))
                    ]
                    
                    if all(success_conditions):
                        self.log_test("GET Specific Invoice - New Fields", True, 
                                    f"Retrieved invoice {data.get('invoice_number')} with all new fields: title='{data.get('invoice_title')}', supervisor='{data.get('supervisor_name')}'")
                    else:
                        failed_conditions = []
                        condition_names = ["id_match", "invoice_title", "supervisor_name", "subtotal", "discount", "discount_type", "discount_value", "total_after_discount", "items_count"]
                        for i, condition in enumerate(success_conditions):
                            if not condition:
                                failed_conditions.append(condition_names[i])
                        
                        self.log_test("GET Specific Invoice - New Fields", False, f"Failed conditions: {failed_conditions}")
                else:
                    self.log_test("GET Specific Invoice - New Fields", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("GET Specific Invoice - New Fields", False, f"Exception: {str(e)}")
    
    def test_data_persistence_and_work_order_integration(self):
        """Test that new invoice fields persist correctly and integrate with work orders"""
        print("\n=== Testing Data Persistence and Work Order Integration ===")
        
        if not self.created_data['invoices']:
            self.log_test("Data Persistence", False, "No invoices available for persistence testing")
            return
        
        # Test that invoices are automatically added to daily work orders with new fields
        today = datetime.now().date().isoformat()
        
        try:
            response = self.session.get(f"{BACKEND_URL}/work-orders/daily/{today}")
            
            if response.status_code == 200:
                work_order = response.json()
                
                # Check if our test invoices are in the daily work order
                work_order_invoices = work_order.get('invoices', [])
                test_invoice_numbers = [inv.get('invoice_number') for inv in self.created_data['invoices']]
                
                found_invoices = []
                for wo_invoice in work_order_invoices:
                    if wo_invoice.get('invoice_number') in test_invoice_numbers:
                        found_invoices.append(wo_invoice)
                
                if len(found_invoices) >= 1:  # At least one of our test invoices should be there
                    # Verify that the invoice in work order has all new fields
                    test_invoice = found_invoices[0]
                    
                    success_conditions = [
                        'invoice_title' in test_invoice,
                        'supervisor_name' in test_invoice,
                        'subtotal' in test_invoice,
                        'discount' in test_invoice,
                        'total_after_discount' in test_invoice,
                        len(test_invoice.get('items', [])) > 0
                    ]
                    
                    # Check items have correct product types and fields
                    items_valid = True
                    for item in test_invoice.get('items', []):
                        if 'product_type' not in item:
                            items_valid = False
                            break
                        
                        if item.get('product_type') == 'local':
                            if not all(field in item for field in ['supplier', 'purchase_price', 'selling_price']):
                                items_valid = False
                                break
                        elif item.get('product_type') == 'manufactured':
                            if not all(field in item for field in ['seal_type', 'material_type']):
                                items_valid = False
                                break
                    
                    success_conditions.append(items_valid)
                    
                    if all(success_conditions):
                        self.log_test("Work Order Integration", True, 
                                    f"Invoice {test_invoice.get('invoice_number')} in daily work order with all new fields preserved")
                    else:
                        self.log_test("Work Order Integration", False, "Some new fields missing in work order invoice")
                else:
                    self.log_test("Work Order Integration", False, f"Test invoices not found in daily work order. Expected: {test_invoice_numbers}")
            else:
                self.log_test("Work Order Integration", False, f"Failed to get daily work order: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Work Order Integration", False, f"Exception: {str(e)}")
        
        # Test data persistence by retrieving invoices again after some time
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            
            if response.status_code == 200:
                all_invoices = response.json()
                test_invoice_numbers = [inv.get('invoice_number') for inv in self.created_data['invoices']]
                persistent_invoices = [inv for inv in all_invoices if inv.get('invoice_number') in test_invoice_numbers]
                
                if len(persistent_invoices) == len(self.created_data['invoices']):
                    # Verify all data is still intact
                    data_intact = True
                    for persistent_inv in persistent_invoices:
                        original_inv = next((inv for inv in self.created_data['invoices'] if inv.get('invoice_number') == persistent_inv.get('invoice_number')), None)
                        
                        if original_inv:
                            if (persistent_inv.get('invoice_title') != original_inv.get('invoice_title') or
                                persistent_inv.get('supervisor_name') != original_inv.get('supervisor_name') or
                                abs(persistent_inv.get('total_amount', 0) - original_inv.get('total_amount', 0)) > 0.1):
                                data_intact = False
                                break
                    
                    if data_intact:
                        self.log_test("Data Persistence", True, "All invoice data persisted correctly in MongoDB")
                    else:
                        self.log_test("Data Persistence", False, "Some invoice data was not persisted correctly")
                else:
                    self.log_test("Data Persistence", False, f"Expected {len(self.created_data['invoices'])} invoices, found {len(persistent_invoices)}")
            else:
                self.log_test("Data Persistence", False, f"Failed to retrieve invoices for persistence test: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Data Persistence", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all new invoice feature tests"""
        print("🚀 Starting New Invoice Features Testing")
        print("=" * 60)
        
        # Setup test data
        self.setup_test_data()
        
        # Run all tests
        self.test_invoice_with_manufactured_products_only()
        self.test_invoice_with_local_products_only()
        self.test_invoice_with_mixed_products()
        self.test_invoice_retrieval_with_new_fields()
        self.test_data_persistence_and_work_order_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 NEW INVOICE FEATURES TEST COMPLETED")
        return success_rate >= 80  # Consider successful if 80% or more tests pass

if __name__ == "__main__":
    tester = NewInvoiceFeaturesTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)