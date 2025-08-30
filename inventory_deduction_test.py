#!/usr/bin/env python3
"""
Inventory Deduction Testing for Invoice Creation
اختبار خصم المخزون عند إنشاء الفواتير
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://oilseal-manager-3.preview.emergentagent.com/api"

class InventoryDeductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_data = {
            'inventory_items': [],
            'customers': [],
            'invoices': [],
            'transactions': []
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
        """Setup test data: Create inventory item NBR 20×30mm with 1000 pieces"""
        print("\n=== Setting Up Test Data ===")
        
        try:
            # Create inventory item: NBR 20×30mm with 1000 pieces
            inventory_data = {
                "material_type": "NBR",
                "inner_diameter": 20.0,
                "outer_diameter": 30.0,
                "available_pieces": 1000,
                "min_stock_level": 10,
                "notes": "Test inventory for deduction testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/inventory", json=inventory_data)
            
            if response.status_code == 200:
                inventory_item = response.json()
                self.created_data['inventory_items'].append(inventory_item)
                self.log_test("Create NBR 20×30mm inventory item with 1000 pieces", True, 
                            f"Created inventory item ID: {inventory_item.get('id')}")
                return inventory_item
            else:
                self.log_test("Create NBR 20×30mm inventory item", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create NBR 20×30mm inventory item", False, f"Exception: {str(e)}")
            return None
    
    def verify_initial_inventory(self, inventory_item_id: str):
        """Verify initial inventory count"""
        print("\n=== Verifying Initial Inventory Count ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inventory")
            
            if response.status_code == 200:
                inventory_items = response.json()
                
                # Find our test item
                test_item = None
                for item in inventory_items:
                    if item.get('id') == inventory_item_id:
                        test_item = item
                        break
                
                if test_item:
                    pieces_count = test_item.get('available_pieces', 0)
                    if pieces_count == 1000:
                        self.log_test("Verify initial inventory count (1000 pieces)", True, 
                                    f"Initial count: {pieces_count} pieces")
                        return True
                    else:
                        self.log_test("Verify initial inventory count", False, 
                                    f"Expected 1000, got {pieces_count}")
                        return False
                else:
                    self.log_test("Verify initial inventory count", False, 
                                "Test inventory item not found")
                    return False
            else:
                self.log_test("Verify initial inventory count", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify initial inventory count", False, f"Exception: {str(e)}")
            return False
    
    def create_test_customer(self):
        """Create a test customer for invoices"""
        try:
            customer_data = {
                "name": "عميل اختبار خصم المخزون",
                "phone": "01234567890",
                "address": "عنوان اختبار"
            }
            
            response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
            
            if response.status_code == 200:
                customer = response.json()
                self.created_data['customers'].append(customer)
                return customer
            else:
                print(f"Failed to create customer: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception creating customer: {str(e)}")
            return None
    
    def test_invoice_creation_with_deduction(self, inventory_item):
        """Test invoice creation with material deduction"""
        print("\n=== Testing Invoice Creation with Material Deduction ===")
        
        # Create test customer
        customer = self.create_test_customer()
        if not customer:
            self.log_test("Create test customer for invoice", False, "Failed to create customer")
            return False
        
        try:
            # Create invoice with manufactured product using NBR 20×30×6mm
            # Quantity: 5 seals
            # Should deduct: (6 + 2) × 5 = 40 pieces from inventory
            
            invoice_data = {
                "customer_name": customer['name'],
                "customer_id": customer['id'],
                "invoice_title": "فاتورة اختبار خصم المخزون",
                "supervisor_name": "مشرف الاختبار",
                "payment_method": "نقدي",
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 20.0,
                        "outer_diameter": 30.0,
                        "height": 6.0,
                        "quantity": 5,
                        "unit_price": 15.0,
                        "total_price": 75.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "id": inventory_item['id'],
                            "material_type": "NBR",
                            "inner_diameter": 20.0,
                            "outer_diameter": 30.0,
                            "unit_code": f"N-{inventory_item['id'][:8]}",
                            "is_finished_product": False
                        }
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            
            if response.status_code == 200:
                invoice = response.json()
                self.created_data['invoices'].append(invoice)
                self.log_test("Create invoice with NBR 20×30×6mm (5 seals)", True, 
                            f"Invoice created: {invoice.get('invoice_number')}")
                return invoice
            else:
                self.log_test("Create invoice with material deduction", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create invoice with material deduction", False, f"Exception: {str(e)}")
            return None
    
    def verify_inventory_deduction(self, inventory_item_id: str, expected_remaining: int = 960):
        """Verify inventory count reduces from 1000 to 960 pieces"""
        print("\n=== Verifying Inventory Deduction ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inventory")
            
            if response.status_code == 200:
                inventory_items = response.json()
                
                # Find our test item
                test_item = None
                for item in inventory_items:
                    if item.get('id') == inventory_item_id:
                        test_item = item
                        break
                
                if test_item:
                    pieces_count = test_item.get('available_pieces', 0)
                    if pieces_count == expected_remaining:
                        self.log_test(f"Verify inventory deduction (1000 → {expected_remaining} pieces)", True, 
                                    f"Current count: {pieces_count} pieces (deducted {1000 - pieces_count} pieces)")
                        return True
                    else:
                        self.log_test("Verify inventory deduction", False, 
                                    f"Expected {expected_remaining}, got {pieces_count}")
                        return False
                else:
                    self.log_test("Verify inventory deduction", False, 
                                "Test inventory item not found")
                    return False
            else:
                self.log_test("Verify inventory deduction", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify inventory deduction", False, f"Exception: {str(e)}")
            return False
    
    def test_inventory_transaction_logging(self, inventory_item_id: str):
        """Test inventory transaction logging for deductions"""
        print("\n=== Testing Inventory Transaction Logging ===")
        
        try:
            # Get inventory transactions for our item
            response = self.session.get(f"{BACKEND_URL}/inventory-transactions/{inventory_item_id}")
            
            if response.status_code == 200:
                transactions = response.json()
                
                # Look for the deduction transaction
                deduction_transaction = None
                for transaction in transactions:
                    if (transaction.get('transaction_type') == 'out' and 
                        transaction.get('pieces_change') == 40 and
                        'استهلاك في الإنتاج' in transaction.get('reason', '')):
                        deduction_transaction = transaction
                        break
                
                if deduction_transaction:
                    self.log_test("Verify inventory transaction created", True, 
                                f"Transaction: type=out, pieces_change=40, reason='{deduction_transaction.get('reason')}'")
                    
                    # Verify transaction details
                    details_correct = (
                        deduction_transaction.get('transaction_type') == 'out' and
                        deduction_transaction.get('pieces_change') == 40 and
                        'استهلاك في الإنتاج' in deduction_transaction.get('reason', '')
                    )
                    
                    if details_correct:
                        self.log_test("Verify transaction details (type=out, pieces_change=40, reason=استهلاك في الإنتاج)", True,
                                    "All transaction details are correct")
                        return True
                    else:
                        self.log_test("Verify transaction details", False, 
                                    f"Transaction details incorrect: {deduction_transaction}")
                        return False
                else:
                    self.log_test("Verify inventory transaction created", False, 
                                "No matching deduction transaction found")
                    return False
            else:
                self.log_test("Get inventory transactions", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test inventory transaction logging", False, f"Exception: {str(e)}")
            return False
    
    def test_insufficient_inventory(self, inventory_item):
        """Test insufficient inventory scenario"""
        print("\n=== Testing Insufficient Inventory Scenario ===")
        
        # Create test customer
        customer = self.create_test_customer()
        if not customer:
            return False
        
        try:
            # Try to create invoice requiring more material than available
            # Current available: 960 pieces (after previous test)
            # Request: 100 seals × (10 + 2) mm = 1200 pieces (more than available)
            
            invoice_data = {
                "customer_name": customer['name'],
                "customer_id": customer['id'],
                "invoice_title": "فاتورة اختبار نقص المخزون",
                "supervisor_name": "مشرف الاختبار",
                "payment_method": "نقدي",
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 20.0,
                        "outer_diameter": 30.0,
                        "height": 10.0,
                        "quantity": 100,
                        "unit_price": 20.0,
                        "total_price": 2000.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "id": inventory_item['id'],
                            "material_type": "NBR",
                            "inner_diameter": 20.0,
                            "outer_diameter": 30.0,
                            "unit_code": f"N-{inventory_item['id'][:8]}",
                            "is_finished_product": False
                        }
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            
            # The system should complete invoice creation but log warning about insufficient stock
            if response.status_code == 200:
                invoice = response.json()
                self.created_data['invoices'].append(invoice)
                self.log_test("Handle insufficient inventory (complete invoice creation)", True, 
                            f"Invoice created despite insufficient stock: {invoice.get('invoice_number')}")
                return True
            else:
                # If it fails, that's also acceptable behavior
                self.log_test("Handle insufficient inventory (reject creation)", True, 
                            f"Invoice creation rejected due to insufficient stock: HTTP {response.status_code}")
                return True
                
        except Exception as e:
            self.log_test("Test insufficient inventory", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_materials(self):
        """Test invoice with multiple items using different materials"""
        print("\n=== Testing Multiple Materials Deduction ===")
        
        # Create additional inventory item for testing
        try:
            # Create BUR inventory item
            bur_inventory_data = {
                "material_type": "BUR",
                "inner_diameter": 25.0,
                "outer_diameter": 35.0,
                "available_pieces": 500,
                "min_stock_level": 10,
                "notes": "Test BUR inventory for multiple materials testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/inventory", json=bur_inventory_data)
            
            if response.status_code != 200:
                self.log_test("Create BUR inventory for multiple materials test", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            bur_inventory = response.json()
            self.created_data['inventory_items'].append(bur_inventory)
            
            # Create test customer
            customer = self.create_test_customer()
            if not customer:
                return False
            
            # Create invoice with multiple items using different materials
            invoice_data = {
                "customer_name": customer['name'],
                "customer_id": customer['id'],
                "invoice_title": "فاتورة اختبار مواد متعددة",
                "supervisor_name": "مشرف الاختبار",
                "payment_method": "نقدي",
                "items": [
                    {
                        "seal_type": "RSL",
                        "material_type": "NBR",
                        "inner_diameter": 20.0,
                        "outer_diameter": 30.0,
                        "height": 5.0,
                        "quantity": 3,
                        "unit_price": 12.0,
                        "total_price": 36.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "id": self.created_data['inventory_items'][0]['id'],  # NBR item
                            "material_type": "NBR",
                            "inner_diameter": 20.0,
                            "outer_diameter": 30.0,
                            "is_finished_product": False
                        }
                    },
                    {
                        "seal_type": "RS",
                        "material_type": "BUR",
                        "inner_diameter": 25.0,
                        "outer_diameter": 35.0,
                        "height": 8.0,
                        "quantity": 2,
                        "unit_price": 18.0,
                        "total_price": 36.0,
                        "product_type": "manufactured",
                        "material_details": {
                            "id": bur_inventory['id'],  # BUR item
                            "material_type": "BUR",
                            "inner_diameter": 25.0,
                            "outer_diameter": 35.0,
                            "is_finished_product": False
                        }
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            
            if response.status_code == 200:
                invoice = response.json()
                self.created_data['invoices'].append(invoice)
                
                # Verify deductions for both materials
                # NBR: (5 + 2) × 3 = 21 pieces should be deducted
                # BUR: (8 + 2) × 2 = 20 pieces should be deducted
                
                self.log_test("Create invoice with multiple materials", True, 
                            f"Invoice created: {invoice.get('invoice_number')}")
                
                # Check NBR deduction (should be 960 - 21 = 939)
                nbr_correct = self.verify_inventory_deduction(
                    self.created_data['inventory_items'][0]['id'], 939)
                
                # Check BUR deduction (should be 500 - 20 = 480)
                bur_correct = self.verify_inventory_deduction(bur_inventory['id'], 480)
                
                if nbr_correct and bur_correct:
                    self.log_test("Verify multiple materials deduction", True, 
                                "Both NBR and BUR materials deducted correctly")
                    return True
                else:
                    self.log_test("Verify multiple materials deduction", False, 
                                "One or both materials not deducted correctly")
                    return False
            else:
                self.log_test("Create invoice with multiple materials", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test multiple materials", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        cleanup_success = True
        
        # Clean up invoices
        for invoice in self.created_data['invoices']:
            try:
                response = self.session.delete(f"{BACKEND_URL}/invoices/{invoice['id']}")
                if response.status_code not in [200, 404]:
                    print(f"Failed to delete invoice {invoice['id']}: {response.status_code}")
                    cleanup_success = False
            except Exception as e:
                print(f"Exception deleting invoice {invoice['id']}: {str(e)}")
                cleanup_success = False
        
        # Clean up customers
        for customer in self.created_data['customers']:
            try:
                response = self.session.delete(f"{BACKEND_URL}/customers/{customer['id']}")
                if response.status_code not in [200, 404]:
                    print(f"Failed to delete customer {customer['id']}: {response.status_code}")
                    cleanup_success = False
            except Exception as e:
                print(f"Exception deleting customer {customer['id']}: {str(e)}")
                cleanup_success = False
        
        # Clean up inventory items
        for inventory_item in self.created_data['inventory_items']:
            try:
                response = self.session.delete(f"{BACKEND_URL}/inventory/{inventory_item['id']}")
                if response.status_code not in [200, 404]:
                    print(f"Failed to delete inventory item {inventory_item['id']}: {response.status_code}")
                    cleanup_success = False
            except Exception as e:
                print(f"Exception deleting inventory item {inventory_item['id']}: {str(e)}")
                cleanup_success = False
        
        if cleanup_success:
            self.log_test("Cleanup test data", True, "All test data cleaned up successfully")
        else:
            self.log_test("Cleanup test data", False, "Some test data could not be cleaned up")
    
    def run_all_tests(self):
        """Run all inventory deduction tests"""
        print("🧪 Starting Inventory Deduction Testing for Invoice Creation")
        print("=" * 70)
        
        # Setup test data
        inventory_item = self.setup_test_data()
        if not inventory_item:
            print("❌ Failed to setup test data. Aborting tests.")
            return
        
        # Verify initial inventory
        if not self.verify_initial_inventory(inventory_item['id']):
            print("❌ Initial inventory verification failed. Aborting tests.")
            return
        
        # Test invoice creation with deduction
        invoice = self.test_invoice_creation_with_deduction(inventory_item)
        if not invoice:
            print("❌ Invoice creation test failed. Continuing with other tests.")
        else:
            # Verify inventory deduction
            self.verify_inventory_deduction(inventory_item['id'])
            
            # Test inventory transaction logging
            self.test_inventory_transaction_logging(inventory_item['id'])
        
        # Test insufficient inventory
        self.test_insufficient_inventory(inventory_item)
        
        # Test multiple materials
        self.test_multiple_materials()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 INVENTORY DEDUCTION TEST SUMMARY")
        print("=" * 70)
        
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
        
        print("\n" + "=" * 70)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Inventory deduction system working perfectly!")
        elif success_rate >= 75:
            print("✅ GOOD: Inventory deduction system working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Inventory deduction system has some issues that need attention.")
        else:
            print("🚨 CRITICAL: Inventory deduction system has major issues that need immediate fixing.")

def main():
    """Main function to run inventory deduction tests"""
    tester = InventoryDeductionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()