#!/usr/bin/env python3
"""
Invoice Management APIs Testing - Payment Method Change & Invoice Cancellation
اختبار APIs إدارة الفواتير - تحويل طريقة الدفع وإلغاء الفواتير
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

class InvoiceManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_data = {
            'customers': [],
            'raw_materials': [],
            'invoices': [],
            'suppliers': [],
            'local_products': []
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
        """Create test data needed for invoice management testing"""
        print("\n=== Setting Up Test Data ===")
        
        # Create test customer
        try:
            customer_data = {
                "name": "عميل اختبار إدارة الفواتير",
                "phone": "01234567890",
                "address": "عنوان اختبار"
            }
            response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.created_data['customers'].append(customer)
                self.log_test("Create test customer", True, f"Customer ID: {customer['id']}")
            else:
                self.log_test("Create test customer", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create test customer", False, str(e))
            return False
        
        # Create test raw materials for manufactured products
        try:
            materials = [
                {
                    "material_type": "NBR",
                    "inner_diameter": 25.0,
                    "outer_diameter": 35.0,
                    "height": 100.0,
                    "pieces_count": 10,
                    "cost_per_mm": 1.5
                },
                {
                    "material_type": "BUR", 
                    "inner_diameter": 30.0,
                    "outer_diameter": 40.0,
                    "height": 80.0,
                    "pieces_count": 8,
                    "cost_per_mm": 2.0
                }
            ]
            
            for material_data in materials:
                response = self.session.post(f"{BACKEND_URL}/raw-materials", json=material_data)
                if response.status_code == 200:
                    material = response.json()
                    self.created_data['raw_materials'].append(material)
                    self.log_test(f"Create {material_data['material_type']} material", True, 
                                f"Unit code: {material['unit_code']}")
                else:
                    self.log_test(f"Create {material_data['material_type']} material", False, 
                                f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create test materials", False, str(e))
        
        # Create test supplier and local product
        try:
            supplier_data = {
                "name": "مورد اختبار إدارة الفواتير",
                "phone": "01111111111",
                "address": "عنوان المورد"
            }
            response = self.session.post(f"{BACKEND_URL}/suppliers", json=supplier_data)
            if response.status_code == 200:
                supplier = response.json()
                self.created_data['suppliers'].append(supplier)
                self.log_test("Create test supplier", True, f"Supplier ID: {supplier['id']}")
                
                # Create local product
                local_product_data = {
                    "name": "منتج محلي اختبار إدارة الفواتير",
                    "supplier_id": supplier['id'],
                    "purchase_price": 15.0,
                    "selling_price": 25.0,
                    "current_stock": 50
                }
                response = self.session.post(f"{BACKEND_URL}/local-products", json=local_product_data)
                if response.status_code == 200:
                    local_product = response.json()
                    self.created_data['local_products'].append(local_product)
                    self.log_test("Create test local product", True, f"Product ID: {local_product['id']}")
            else:
                self.log_test("Create test supplier", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create test supplier/local product", False, str(e))
        
        return True
    
    def create_test_invoices(self):
        """Create various types of invoices for testing"""
        print("\n=== Creating Test Invoices ===")
        
        if not self.created_data['customers'] or not self.created_data['raw_materials']:
            self.log_test("Create test invoices", False, "Missing test data")
            return False
        
        customer = self.created_data['customers'][0]
        material = self.created_data['raw_materials'][0]
        
        # Invoice 1: Manufactured product with cash payment
        try:
            invoice_data = {
                "customer_id": customer['id'],
                "customer_name": customer['name'],
                "invoice_title": "فاتورة اختبار منتج مصنع",
                "supervisor_name": "مشرف الاختبار",
                "payment_method": "نقدي",
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 25.0,
                        "outer_diameter": 35.0,
                        "height": 8.0,
                        "quantity": 5,
                        "unit_price": 10.0,
                        "total_price": 50.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "unit_code": material['unit_code'],
                            "material_type": "NBR",
                            "inner_diameter": 25.0,
                            "outer_diameter": 35.0
                        }
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                self.created_data['invoices'].append(invoice)
                self.log_test("Create manufactured product invoice (cash)", True, 
                            f"Invoice: {invoice['invoice_number']}")
            else:
                self.log_test("Create manufactured product invoice (cash)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create manufactured product invoice (cash)", False, str(e))
        
        # Invoice 2: Multi-material manufactured product with Vodafone payment
        try:
            materials = self.created_data['raw_materials']
            if len(materials) >= 2:
                invoice_data = {
                    "customer_id": customer['id'],
                    "customer_name": customer['name'],
                    "invoice_title": "فاتورة اختبار مواد متعددة",
                    "supervisor_name": "مشرف الاختبار",
                    "payment_method": "فودافون كاش محمد الصاوي",
                    "items": [
                        {
                            "seal_type": "RS",
                            "material_type": "NBR",
                            "inner_diameter": 25.0,
                            "outer_diameter": 35.0,
                            "height": 10.0,
                            "quantity": 8,
                            "unit_price": 12.0,
                            "total_price": 96.0,
                            "product_type": "manufactured",
                            "selected_materials": [
                                {
                                    "unit_code": materials[0]['unit_code'],
                                    "material_type": "NBR",
                                    "inner_diameter": 25.0,
                                    "outer_diameter": 35.0,
                                    "seals_count": 5
                                },
                                {
                                    "unit_code": materials[1]['unit_code'],
                                    "material_type": "BUR",
                                    "inner_diameter": 30.0,
                                    "outer_diameter": 40.0,
                                    "seals_count": 3
                                }
                            ]
                        }
                    ]
                }
                
                response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
                if response.status_code == 200:
                    invoice = response.json()
                    self.created_data['invoices'].append(invoice)
                    self.log_test("Create multi-material invoice (Vodafone)", True, 
                                f"Invoice: {invoice['invoice_number']}")
                else:
                    self.log_test("Create multi-material invoice (Vodafone)", False, 
                                f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create multi-material invoice (Vodafone)", False, str(e))
        
        # Invoice 3: Local product with InstaPay
        try:
            if self.created_data['local_products']:
                local_product = self.created_data['local_products'][0]
                supplier = self.created_data['suppliers'][0]
                
                invoice_data = {
                    "customer_id": customer['id'],
                    "customer_name": customer['name'],
                    "invoice_title": "فاتورة اختبار منتج محلي",
                    "supervisor_name": "مشرف الاختبار",
                    "payment_method": "انستاباي",
                    "items": [
                        {
                            "product_name": local_product['name'],
                            "quantity": 3,
                            "unit_price": 25.0,
                            "total_price": 75.0,
                            "product_type": "local",
                            "supplier": supplier['name'],
                            "purchase_price": 15.0,
                            "selling_price": 25.0,
                            "local_product_details": {
                                "name": local_product['name'],
                                "supplier": supplier['name'],
                                "purchase_price": 15.0,
                                "selling_price": 25.0
                            }
                        }
                    ]
                }
                
                response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
                if response.status_code == 200:
                    invoice = response.json()
                    self.created_data['invoices'].append(invoice)
                    self.log_test("Create local product invoice (InstaPay)", True, 
                                f"Invoice: {invoice['invoice_number']}")
                else:
                    self.log_test("Create local product invoice (InstaPay)", False, 
                                f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create local product invoice (InstaPay)", False, str(e))
        
        # Invoice 4: Deferred payment invoice
        try:
            invoice_data = {
                "customer_id": customer['id'],
                "customer_name": customer['name'],
                "invoice_title": "فاتورة اختبار آجل",
                "supervisor_name": "مشرف الاختبار",
                "payment_method": "آجل",
                "items": [
                    {
                        "seal_type": "B17",
                        "material_type": "NBR",
                        "inner_diameter": 25.0,
                        "outer_diameter": 35.0,
                        "height": 6.0,
                        "quantity": 10,
                        "unit_price": 8.0,
                        "total_price": 80.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "unit_code": material['unit_code'],
                            "material_type": "NBR",
                            "inner_diameter": 25.0,
                            "outer_diameter": 35.0
                        }
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                self.created_data['invoices'].append(invoice)
                self.log_test("Create deferred payment invoice", True, 
                            f"Invoice: {invoice['invoice_number']}")
            else:
                self.log_test("Create deferred payment invoice", False, 
                            f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create deferred payment invoice", False, str(e))
        
        return len(self.created_data['invoices']) > 0
    
    def test_payment_method_change(self):
        """Test PUT /api/invoices/{invoice_id}/change-payment-method"""
        print("\n=== Testing Payment Method Change API ===")
        
        if not self.created_data['invoices']:
            self.log_test("Payment method change tests", False, "No test invoices available")
            return
        
        # Test 1: Change from cash to Vodafone
        try:
            cash_invoice = None
            for invoice in self.created_data['invoices']:
                if invoice.get('payment_method') == 'نقدي':
                    cash_invoice = invoice
                    break
            
            if cash_invoice:
                # Get treasury balances before change
                response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                if response.status_code == 200:
                    balances_before = response.json()
                    cash_before = balances_before.get('cash', 0)
                    vodafone_before = balances_before.get('vodafone_elsawy', 0)
                    
                    # Change payment method
                    response = self.session.put(
                        f"{BACKEND_URL}/invoices/{cash_invoice['id']}/change-payment-method",
                        params={"new_payment_method": "فودافون كاش محمد الصاوي"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.log_test("Change cash to Vodafone", True, 
                                    f"Amount transferred: {result.get('amount_transferred')}")
                        
                        # Verify treasury transactions
                        response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                        if response.status_code == 200:
                            balances_after = response.json()
                            cash_after = balances_after.get('cash', 0)
                            vodafone_after = balances_after.get('vodafone_elsawy', 0)
                            
                            expected_amount = cash_invoice.get('total_amount', 0)
                            cash_diff = cash_before - cash_after
                            vodafone_diff = vodafone_after - vodafone_before
                            
                            if abs(cash_diff - expected_amount) < 0.01 and abs(vodafone_diff - expected_amount) < 0.01:
                                self.log_test("Treasury transaction verification", True, 
                                            f"Cash reduced by {cash_diff}, Vodafone increased by {vodafone_diff}")
                            else:
                                self.log_test("Treasury transaction verification", False, 
                                            f"Expected: {expected_amount}, Cash diff: {cash_diff}, Vodafone diff: {vodafone_diff}")
                        
                        # Verify invoice payment method updated
                        response = self.session.get(f"{BACKEND_URL}/invoices/{cash_invoice['id']}")
                        if response.status_code == 200:
                            updated_invoice = response.json()
                            if updated_invoice.get('payment_method') == 'فودافون كاش محمد الصاوي':
                                self.log_test("Invoice payment method updated", True)
                            else:
                                self.log_test("Invoice payment method updated", False, 
                                            f"Expected: فودافون كاش محمد الصاوي, Got: {updated_invoice.get('payment_method')}")
                    else:
                        self.log_test("Change cash to Vodafone", False, 
                                    f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_test("Change cash to Vodafone", False, "No cash invoice found")
        except Exception as e:
            self.log_test("Change cash to Vodafone", False, str(e))
        
        # Test 2: Test all payment method combinations
        payment_methods = [
            "نقدي",
            "فودافون كاش محمد الصاوي", 
            "فودافون كاش وائل محمد",
            "انستاباي",
            "يد الصاوي"
        ]
        
        for i, invoice in enumerate(self.created_data['invoices'][:3]):  # Test first 3 invoices
            if invoice.get('payment_method') != 'آجل':  # Skip deferred invoices
                try:
                    current_method = invoice.get('payment_method')
                    # Choose a different method
                    new_method = payment_methods[(payment_methods.index(current_method) + 1) % len(payment_methods)]
                    
                    response = self.session.put(
                        f"{BACKEND_URL}/invoices/{invoice['id']}/change-payment-method",
                        params={"new_payment_method": new_method}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.log_test(f"Change {current_method} to {new_method}", True, 
                                    f"Invoice: {invoice['invoice_number']}")
                    else:
                        self.log_test(f"Change {current_method} to {new_method}", False, 
                                    f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Payment method change test {i+1}", False, str(e))
        
        # Test 3: Invalid payment method
        try:
            if self.created_data['invoices']:
                invoice = self.created_data['invoices'][0]
                response = self.session.put(
                    f"{BACKEND_URL}/invoices/{invoice['id']}/change-payment-method",
                    params={"new_payment_method": "طريقة غير صحيحة"}
                )
                
                if response.status_code == 400:
                    self.log_test("Invalid payment method rejection", True, "Correctly rejected invalid method")
                else:
                    self.log_test("Invalid payment method rejection", False, 
                                f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid payment method test", False, str(e))
        
        # Test 4: Same payment method
        try:
            if self.created_data['invoices']:
                invoice = self.created_data['invoices'][0]
                current_method = invoice.get('payment_method')
                
                response = self.session.put(
                    f"{BACKEND_URL}/invoices/{invoice['id']}/change-payment-method",
                    params={"new_payment_method": current_method}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "نفسها بالفعل" in result.get('message', ''):
                        self.log_test("Same payment method handling", True, "Correctly handled same method")
                    else:
                        self.log_test("Same payment method handling", False, 
                                    f"Unexpected message: {result.get('message')}")
                else:
                    self.log_test("Same payment method handling", False, 
                                f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Same payment method test", False, str(e))
    
    def test_invoice_cancellation(self):
        """Test DELETE /api/invoices/{invoice_id}/cancel"""
        print("\n=== Testing Invoice Cancellation API ===")
        
        if not self.created_data['invoices']:
            self.log_test("Invoice cancellation tests", False, "No test invoices available")
            return
        
        # Test 1: Cancel manufactured product invoice (material restoration)
        try:
            manufactured_invoice = None
            for invoice in self.created_data['invoices']:
                if any(item.get('product_type') == 'manufactured' for item in invoice.get('items', [])):
                    manufactured_invoice = invoice
                    break
            
            if manufactured_invoice:
                # Get material heights before cancellation
                materials_before = {}
                for item in manufactured_invoice.get('items', []):
                    if item.get('material_details'):
                        unit_code = item['material_details'].get('unit_code')
                        if unit_code:
                            response = self.session.get(f"{BACKEND_URL}/raw-materials")
                            if response.status_code == 200:
                                materials = response.json()
                                for material in materials:
                                    if material.get('unit_code') == unit_code:
                                        materials_before[unit_code] = material.get('height', 0)
                                        break
                
                # Cancel the invoice
                response = self.session.delete(f"{BACKEND_URL}/invoices/{manufactured_invoice['id']}/cancel")
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Cancel manufactured product invoice", True, 
                                f"Invoice: {result.get('invoice_number')}")
                    
                    # Verify material restoration
                    if result.get('materials_restored'):
                        for item in manufactured_invoice.get('items', []):
                            if item.get('material_details'):
                                unit_code = item['material_details'].get('unit_code')
                                if unit_code and unit_code in materials_before:
                                    response = self.session.get(f"{BACKEND_URL}/raw-materials")
                                    if response.status_code == 200:
                                        materials = response.json()
                                        for material in materials:
                                            if material.get('unit_code') == unit_code:
                                                height_after = material.get('height', 0)
                                                height_before = materials_before[unit_code]
                                                expected_restoration = item.get('quantity', 0) * (item.get('height', 0) + 2)
                                                actual_restoration = height_after - height_before
                                                
                                                if abs(actual_restoration - expected_restoration) < 0.01:
                                                    self.log_test("Material restoration verification", True, 
                                                                f"Restored {actual_restoration}mm to {unit_code}")
                                                else:
                                                    self.log_test("Material restoration verification", False, 
                                                                f"Expected: {expected_restoration}mm, Actual: {actual_restoration}mm")
                                                break
                    
                    # Verify invoice deleted
                    response = self.session.get(f"{BACKEND_URL}/invoices/{manufactured_invoice['id']}")
                    if response.status_code == 404:
                        self.log_test("Invoice deletion verification", True, "Invoice successfully deleted")
                    else:
                        self.log_test("Invoice deletion verification", False, 
                                    f"Invoice still exists, status: {response.status_code}")
                else:
                    self.log_test("Cancel manufactured product invoice", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_test("Cancel manufactured product invoice", False, "No manufactured invoice found")
        except Exception as e:
            self.log_test("Cancel manufactured product invoice", False, str(e))
        
        # Test 2: Cancel multi-material invoice
        try:
            multi_material_invoice = None
            for invoice in self.created_data['invoices']:
                for item in invoice.get('items', []):
                    if item.get('selected_materials'):
                        multi_material_invoice = invoice
                        break
                if multi_material_invoice:
                    break
            
            if multi_material_invoice:
                response = self.session.delete(f"{BACKEND_URL}/invoices/{multi_material_invoice['id']}/cancel")
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Cancel multi-material invoice", True, 
                                f"Invoice: {result.get('invoice_number')}")
                    
                    if result.get('materials_restored'):
                        self.log_test("Multi-material restoration", True, "Materials restored successfully")
                    else:
                        self.log_test("Multi-material restoration", False, "Materials not restored")
                else:
                    self.log_test("Cancel multi-material invoice", False, 
                                f"Status: {response.status_code}")
            else:
                self.log_test("Cancel multi-material invoice", False, "No multi-material invoice found")
        except Exception as e:
            self.log_test("Cancel multi-material invoice", False, str(e))
        
        # Test 3: Cancel local product invoice
        try:
            local_invoice = None
            for invoice in self.created_data['invoices']:
                if any(item.get('product_type') == 'local' for item in invoice.get('items', [])):
                    local_invoice = invoice
                    break
            
            if local_invoice:
                response = self.session.delete(f"{BACKEND_URL}/invoices/{local_invoice['id']}/cancel")
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Cancel local product invoice", True, 
                                f"Invoice: {result.get('invoice_number')}")
                else:
                    self.log_test("Cancel local product invoice", False, 
                                f"Status: {response.status_code}")
            else:
                self.log_test("Cancel local product invoice", False, "No local product invoice found")
        except Exception as e:
            self.log_test("Cancel local product invoice", False, str(e))
        
        # Test 4: Cancel non-deferred invoice (treasury reversal)
        try:
            non_deferred_invoice = None
            for invoice in self.created_data['invoices']:
                if invoice.get('payment_method') != 'آجل':
                    non_deferred_invoice = invoice
                    break
            
            if non_deferred_invoice:
                # Get treasury balance before cancellation
                payment_method = non_deferred_invoice.get('payment_method')
                account_mapping = {
                    "نقدي": "cash",
                    "فودافون كاش محمد الصاوي": "vodafone_elsawy",
                    "فودافون كاش وائل محمد": "vodafone_wael",
                    "انستاباي": "instapay",
                    "يد الصاوي": "yad_elsawy"
                }
                
                account_id = account_mapping.get(payment_method)
                if account_id:
                    response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                    if response.status_code == 200:
                        balances_before = response.json()
                        balance_before = balances_before.get(account_id, 0)
                        
                        # Cancel the invoice
                        response = self.session.delete(f"{BACKEND_URL}/invoices/{non_deferred_invoice['id']}/cancel")
                        
                        if response.status_code == 200:
                            result = response.json()
                            self.log_test("Cancel non-deferred invoice", True, 
                                        f"Invoice: {result.get('invoice_number')}")
                            
                            if result.get('treasury_reversed'):
                                # Verify treasury reversal
                                response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                                if response.status_code == 200:
                                    balances_after = response.json()
                                    balance_after = balances_after.get(account_id, 0)
                                    expected_reduction = non_deferred_invoice.get('total_amount', 0)
                                    actual_reduction = balance_before - balance_after
                                    
                                    if abs(actual_reduction - expected_reduction) < 0.01:
                                        self.log_test("Treasury reversal verification", True, 
                                                    f"Reduced {actual_reduction} from {account_id}")
                                    else:
                                        self.log_test("Treasury reversal verification", False, 
                                                    f"Expected: {expected_reduction}, Actual: {actual_reduction}")
                            else:
                                self.log_test("Treasury reversal flag", False, "Treasury not marked as reversed")
                        else:
                            self.log_test("Cancel non-deferred invoice", False, 
                                        f"Status: {response.status_code}")
            else:
                self.log_test("Cancel non-deferred invoice", False, "No non-deferred invoice found")
        except Exception as e:
            self.log_test("Cancel non-deferred invoice", False, str(e))
        
        # Test 5: Cancel deferred invoice (no treasury reversal)
        try:
            deferred_invoice = None
            for invoice in self.created_data['invoices']:
                if invoice.get('payment_method') == 'آجل':
                    deferred_invoice = invoice
                    break
            
            if deferred_invoice:
                response = self.session.delete(f"{BACKEND_URL}/invoices/{deferred_invoice['id']}/cancel")
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("Cancel deferred invoice", True, 
                                f"Invoice: {result.get('invoice_number')}")
                    
                    if not result.get('treasury_reversed'):
                        self.log_test("Deferred treasury handling", True, "Correctly no treasury reversal for deferred")
                    else:
                        self.log_test("Deferred treasury handling", False, "Unexpected treasury reversal for deferred")
                else:
                    self.log_test("Cancel deferred invoice", False, 
                                f"Status: {response.status_code}")
            else:
                self.log_test("Cancel deferred invoice", False, "No deferred invoice found")
        except Exception as e:
            self.log_test("Cancel deferred invoice", False, str(e))
        
        # Test 6: Cancel non-existent invoice
        try:
            response = self.session.delete(f"{BACKEND_URL}/invoices/non-existent-id/cancel")
            
            if response.status_code == 404:
                self.log_test("Cancel non-existent invoice", True, "Correctly returned 404")
            else:
                self.log_test("Cancel non-existent invoice", False, 
                            f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Cancel non-existent invoice", False, str(e))
    
    def test_data_consistency(self):
        """Test data consistency across collections after operations"""
        print("\n=== Testing Data Consistency ===")
        
        try:
            # Check invoices collection
            response = self.session.get(f"{BACKEND_URL}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                self.log_test("Invoices collection accessible", True, f"Found {len(invoices)} invoices")
            else:
                self.log_test("Invoices collection accessible", False, f"Status: {response.status_code}")
            
            # Check treasury transactions
            response = self.session.get(f"{BACKEND_URL}/treasury/transactions")
            if response.status_code == 200:
                transactions = response.json()
                self.log_test("Treasury transactions accessible", True, f"Found {len(transactions)} transactions")
            else:
                self.log_test("Treasury transactions accessible", False, f"Status: {response.status_code}")
            
            # Check raw materials
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            if response.status_code == 200:
                materials = response.json()
                self.log_test("Raw materials accessible", True, f"Found {len(materials)} materials")
            else:
                self.log_test("Raw materials accessible", False, f"Status: {response.status_code}")
            
            # Check work orders
            response = self.session.get(f"{BACKEND_URL}/work-orders")
            if response.status_code == 200:
                work_orders = response.json()
                self.log_test("Work orders accessible", True, f"Found {len(work_orders)} work orders")
            else:
                self.log_test("Work orders accessible", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Data consistency check", False, str(e))
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Note: Some invoices may have been deleted during cancellation tests
        # Clean up remaining invoices
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                for invoice in invoices:
                    if "اختبار" in invoice.get('invoice_title', '') or "اختبار" in invoice.get('customer_name', ''):
                        try:
                            self.session.delete(f"{BACKEND_URL}/invoices/{invoice['id']}")
                        except:
                            pass
        except:
            pass
        
        # Clean up customers
        for customer in self.created_data['customers']:
            try:
                self.session.delete(f"{BACKEND_URL}/customers/{customer['id']}")
            except:
                pass
        
        # Clean up suppliers
        for supplier in self.created_data['suppliers']:
            try:
                self.session.delete(f"{BACKEND_URL}/suppliers/{supplier['id']}")
            except:
                pass
        
        # Clean up local products
        for product in self.created_data['local_products']:
            try:
                self.session.delete(f"{BACKEND_URL}/local-products/{product['id']}")
            except:
                pass
        
        # Note: Raw materials are not cleaned up as they may be needed by other tests
        # and material restoration during cancellation tests should have restored them
        
        self.log_test("Test data cleanup", True, "Cleanup completed")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("INVOICE MANAGEMENT API TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['details']}")
        
        print("\n" + "="*60)
        
        return success_rate >= 80  # Consider 80%+ as overall success
    
    def run_all_tests(self):
        """Run all invoice management tests"""
        print("Starting Invoice Management API Tests...")
        print("Testing PUT /api/invoices/{id}/change-payment-method and DELETE /api/invoices/{id}/cancel")
        
        # Setup
        if not self.setup_test_data():
            print("❌ Failed to setup test data. Aborting tests.")
            return False
        
        if not self.create_test_invoices():
            print("❌ Failed to create test invoices. Aborting tests.")
            return False
        
        # Run tests
        self.test_payment_method_change()
        self.test_invoice_cancellation()
        self.test_data_consistency()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        return self.print_summary()

def main():
    """Main function"""
    tester = InvoiceManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Invoice Management API tests completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some Invoice Management API tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()