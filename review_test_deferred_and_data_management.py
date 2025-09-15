#!/usr/bin/env python3
"""
Backend API Testing for Master Seal System - Review Request Focus
Testing specific requirements from review request:
1. Fix for "الآجل" payment method change issue
2. New Data Management APIs testing
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

class ReviewFocusedTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
    def test_payment_method_change_fix(self):
        """Test the fix for 'الآجل' payment method change issue"""
        print("\n🔧 Testing Payment Method Change Fix for 'الآجل'...")
        
        try:
            # First, create a test customer
            customer_data = {
                "name": "عميل اختبار تحويل الدفع",
                "phone": "01234567890",
                "address": "عنوان اختبار"
            }
            
            customer_response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
            if customer_response.status_code != 200:
                self.log_test("Create test customer for payment change", False, f"HTTP {customer_response.status_code}")
                return
            
            customer = customer_response.json()
            self.log_test("Create test customer for payment change", True, f"Customer ID: {customer['id']}")
            
            # Create test invoices with different payment methods
            test_invoices = []
            
            # 1. Create cash invoice
            cash_invoice_data = {
                "customer_name": customer["name"],
                "customer_id": customer["id"],
                "items": [{
                    "seal_type": "RSL",
                    "material_type": "NBR",
                    "inner_diameter": 20.0,
                    "outer_diameter": 30.0,
                    "height": 8.0,
                    "quantity": 5,
                    "unit_price": 10.0,
                    "total_price": 50.0,
                    "product_type": "manufactured"
                }],
                "payment_method": "نقدي",
                "discount_type": "amount",
                "discount_value": 0.0
            }
            
            cash_response = self.session.post(f"{BACKEND_URL}/invoices", json=cash_invoice_data)
            if cash_response.status_code == 200:
                cash_invoice = cash_response.json()
                test_invoices.append(("cash", cash_invoice))
                self.log_test("Create cash invoice for payment change test", True, f"Invoice: {cash_invoice['invoice_number']}")
            else:
                self.log_test("Create cash invoice for payment change test", False, f"HTTP {cash_response.status_code}")
                return
            
            # 2. Create deferred invoice
            deferred_invoice_data = {
                "customer_name": customer["name"],
                "customer_id": customer["id"],
                "items": [{
                    "seal_type": "RS",
                    "material_type": "BUR",
                    "inner_diameter": 25.0,
                    "outer_diameter": 35.0,
                    "height": 10.0,
                    "quantity": 3,
                    "unit_price": 15.0,
                    "total_price": 45.0,
                    "product_type": "manufactured"
                }],
                "payment_method": "آجل",
                "discount_type": "amount",
                "discount_value": 0.0
            }
            
            deferred_response = self.session.post(f"{BACKEND_URL}/invoices", json=deferred_invoice_data)
            if deferred_response.status_code == 200:
                deferred_invoice = deferred_response.json()
                test_invoices.append(("deferred", deferred_invoice))
                self.log_test("Create deferred invoice for payment change test", True, f"Invoice: {deferred_invoice['invoice_number']}")
            else:
                self.log_test("Create deferred invoice for payment change test", False, f"HTTP {deferred_response.status_code}")
                return
            
            # Test payment method changes
            print("\n📋 Testing Payment Method Changes...")
            
            # Test 1: Convert cash to deferred (آجل)
            cash_invoice_id = test_invoices[0][1]["id"]
            change_response = self.session.put(
                f"{BACKEND_URL}/invoices/{cash_invoice_id}/change-payment-method",
                params={"new_payment_method": "آجل", "username": "test"}
            )
            
            if change_response.status_code == 200:
                result = change_response.json()
                if "طريقة الدفع غير مدعومة" not in result.get("message", ""):
                    self.log_test("Convert cash to آجل", True, f"Success: {result.get('message', '')}")
                else:
                    self.log_test("Convert cash to آجل", False, "Got unsupported payment method error")
            else:
                self.log_test("Convert cash to آجل", False, f"HTTP {change_response.status_code}: {change_response.text}")
            
            # Test 2: Convert deferred (آجل) to cash
            deferred_invoice_id = test_invoices[1][1]["id"]
            change_response = self.session.put(
                f"{BACKEND_URL}/invoices/{deferred_invoice_id}/change-payment-method",
                params={"new_payment_method": "نقدي", "username": "test"}
            )
            
            if change_response.status_code == 200:
                result = change_response.json()
                if "طريقة الدفع غير مدعومة" not in result.get("message", ""):
                    self.log_test("Convert آجل to cash", True, f"Success: {result.get('message', '')}")
                else:
                    self.log_test("Convert آجل to cash", False, "Got unsupported payment method error")
            else:
                self.log_test("Convert آجل to cash", False, f"HTTP {change_response.status_code}: {change_response.text}")
            
            # Test 3: Convert deferred (آجل) to Vodafone Cash
            change_response = self.session.put(
                f"{BACKEND_URL}/invoices/{deferred_invoice_id}/change-payment-method",
                params={"new_payment_method": "فودافون كاش محمد الصاوي", "username": "test"}
            )
            
            if change_response.status_code == 200:
                result = change_response.json()
                if "طريقة الدفع غير مدعومة" not in result.get("message", ""):
                    self.log_test("Convert آجل to Vodafone Cash", True, f"Success: {result.get('message', '')}")
                else:
                    self.log_test("Convert آجل to Vodafone Cash", False, "Got unsupported payment method error")
            else:
                self.log_test("Convert آجل to Vodafone Cash", False, f"HTTP {change_response.status_code}: {change_response.text}")
            
            # Test 4: Verify no "طريقة الدفع غير مدعومة" message appears
            # Test with all supported payment methods
            supported_methods = [
                "نقدي",
                "آجل", 
                "فودافون كاش محمد الصاوي",
                "فودافون كاش وائل محمد",
                "انستاباي",
                "يد الصاوي"
            ]
            
            unsupported_errors = 0
            for method in supported_methods:
                change_response = self.session.put(
                    f"{BACKEND_URL}/invoices/{cash_invoice_id}/change-payment-method",
                    params={"new_payment_method": method, "username": "test"}
                )
                
                if change_response.status_code == 200:
                    result = change_response.json()
                    if "طريقة الدفع غير مدعومة" in result.get("message", ""):
                        unsupported_errors += 1
                        
            if unsupported_errors == 0:
                self.log_test("No 'unsupported payment method' errors", True, f"All {len(supported_methods)} methods supported")
            else:
                self.log_test("No 'unsupported payment method' errors", False, f"{unsupported_errors} methods showed unsupported error")
                
        except Exception as e:
            self.log_test("Payment method change testing", False, f"Exception: {str(e)}")
    
    def test_data_management_apis(self):
        """Test new Data Management APIs"""
        print("\n📊 Testing Data Management APIs...")
        
        # Test 1: Export All Data
        try:
            export_response = self.session.get(f"{BACKEND_URL}/data-management/export-all")
            
            if export_response.status_code == 200:
                export_data = export_response.json()
                
                # Check if export contains expected data structure
                required_fields = ["export_timestamp", "system_version", "data"]
                missing_fields = [field for field in required_fields if field not in export_data]
                
                if not missing_fields:
                    data_types = list(export_data.get("data", {}).keys())
                    self.log_test("GET /api/data-management/export-all", True, f"Export contains: {', '.join(data_types)}")
                else:
                    self.log_test("GET /api/data-management/export-all", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("GET /api/data-management/export-all", False, f"HTTP {export_response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/data-management/export-all", False, f"Exception: {str(e)}")
        
        # Test 2: Bulk Import Raw Materials
        try:
            test_raw_materials = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "material_type": "NBR",
                        "inner_diameter": 15.0,
                        "outer_diameter": 25.0,
                        "height": 100.0,
                        "pieces_count": 10,
                        "unit_code": "TEST-NBR-001",
                        "cost_per_mm": 0.5,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "material_type": "BUR",
                        "inner_diameter": 20.0,
                        "outer_diameter": 30.0,
                        "height": 80.0,
                        "pieces_count": 5,
                        "unit_code": "TEST-BUR-001",
                        "cost_per_mm": 0.7,
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/raw-materials/bulk-import", json=test_raw_materials)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/raw-materials/bulk-import", True, f"Imported {imported} materials")
            else:
                self.log_test("POST /api/raw-materials/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/raw-materials/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 3: Bulk Import Invoices
        try:
            test_invoices = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "invoice_number": f"TEST-INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "customer_name": "عميل اختبار الاستيراد",
                        "items": [{
                            "seal_type": "RSL",
                            "material_type": "NBR",
                            "inner_diameter": 20.0,
                            "outer_diameter": 30.0,
                            "height": 8.0,
                            "quantity": 2,
                            "unit_price": 12.0,
                            "total_price": 24.0,
                            "product_type": "manufactured"
                        }],
                        "total_amount": 24.0,
                        "paid_amount": 0.0,
                        "remaining_amount": 24.0,
                        "payment_method": "آجل",
                        "status": "غير مدفوعة",
                        "date": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/invoices/bulk-import", json=test_invoices)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/invoices/bulk-import", True, f"Imported {imported} invoices")
            else:
                self.log_test("POST /api/invoices/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/invoices/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 4: Bulk Import Treasury Transactions
        try:
            test_treasury = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "account_id": "cash",
                        "transaction_type": "income",
                        "amount": 100.0,
                        "description": "اختبار استيراد معاملة خزينة",
                        "reference": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "date": datetime.now().isoformat(),
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/treasury/transactions/bulk-import", json=test_treasury)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/treasury/transactions/bulk-import", True, f"Imported {imported} transactions")
            else:
                self.log_test("POST /api/treasury/transactions/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/treasury/transactions/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 5: Bulk Import Expenses
        try:
            test_expenses = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "description": "مصروف اختبار الاستيراد",
                        "amount": 50.0,
                        "category": "أخرى",
                        "date": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/expenses/bulk-import", json=test_expenses)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/expenses/bulk-import", True, f"Imported {imported} expenses")
            else:
                self.log_test("POST /api/expenses/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/expenses/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 6: Bulk Import Revenues
        try:
            test_revenues = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "description": "إيراد اختبار الاستيراد",
                        "amount": 200.0,
                        "source": "مبيعات",
                        "date": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/revenues/bulk-import", json=test_revenues)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/revenues/bulk-import", True, f"Imported {imported} revenues")
            else:
                self.log_test("POST /api/revenues/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/revenues/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 7: Bulk Import Work Orders
        try:
            test_work_orders = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "أمر شغل اختبار الاستيراد",
                        "description": "وصف أمر الشغل للاختبار",
                        "supervisor_name": "مشرف الاختبار",
                        "is_daily": False,
                        "invoices": [],
                        "total_amount": 0.0,
                        "total_items": 0,
                        "status": "جديد",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/work-orders/bulk-import", json=test_work_orders)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/work-orders/bulk-import", True, f"Imported {imported} work orders")
            else:
                self.log_test("POST /api/work-orders/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/work-orders/bulk-import", False, f"Exception: {str(e)}")
        
        # Test 8: Bulk Import Pricing
        try:
            test_pricing = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "client_type": "عميل 1",
                        "material_type": "NBR",
                        "price_per_unit": 1.5,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                ]
            }
            
            import_response = self.session.post(f"{BACKEND_URL}/pricing/bulk-import", json=test_pricing)
            
            if import_response.status_code == 200:
                result = import_response.json()
                imported = result.get("imported", 0)
                self.log_test("POST /api/pricing/bulk-import", True, f"Imported {imported} pricing records")
            else:
                self.log_test("POST /api/pricing/bulk-import", False, f"HTTP {import_response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/pricing/bulk-import", False, f"Exception: {str(e)}")
    
    def test_error_handling_and_arabic_messages(self):
        """Test error handling and Arabic messages"""
        print("\n🔍 Testing Error Handling and Arabic Messages...")
        
        # Test invalid payment method change
        try:
            change_response = self.session.put(
                f"{BACKEND_URL}/invoices/invalid-id/change-payment-method",
                params={"new_payment_method": "آجل", "username": "test"}
            )
            
            if change_response.status_code == 404:
                result = change_response.json()
                if "الفاتورة غير موجودة" in result.get("detail", ""):
                    self.log_test("Arabic error message for invalid invoice", True, "Correct Arabic error message")
                else:
                    self.log_test("Arabic error message for invalid invoice", False, f"Got: {result.get('detail', '')}")
            else:
                self.log_test("Arabic error message for invalid invoice", False, f"Expected 404, got {change_response.status_code}")
                
        except Exception as e:
            self.log_test("Arabic error message for invalid invoice", False, f"Exception: {str(e)}")
        
        # Test duplicate prevention in bulk import
        try:
            # Try to import the same raw material twice
            duplicate_data = {
                "data": [
                    {
                        "id": str(uuid.uuid4()),
                        "material_type": "NBR",
                        "inner_diameter": 15.0,
                        "outer_diameter": 25.0,
                        "height": 100.0,
                        "pieces_count": 10,
                        "unit_code": "DUPLICATE-TEST-001",
                        "cost_per_mm": 0.5,
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            # First import
            first_response = self.session.post(f"{BACKEND_URL}/raw-materials/bulk-import", json=duplicate_data)
            
            # Second import (should skip duplicate)
            second_response = self.session.post(f"{BACKEND_URL}/raw-materials/bulk-import", json=duplicate_data)
            
            if first_response.status_code == 200 and second_response.status_code == 200:
                first_result = first_response.json()
                second_result = second_response.json()
                
                if first_result.get("imported", 0) > 0 and second_result.get("skipped", 0) > 0:
                    self.log_test("Duplicate prevention in bulk import", True, f"First: {first_result.get('imported', 0)} imported, Second: {second_result.get('skipped', 0)} skipped")
                else:
                    self.log_test("Duplicate prevention in bulk import", False, f"First: {first_result}, Second: {second_result}")
            else:
                self.log_test("Duplicate prevention in bulk import", False, f"HTTP errors: {first_response.status_code}, {second_response.status_code}")
                
        except Exception as e:
            self.log_test("Duplicate prevention in bulk import", False, f"Exception: {str(e)}")
    
    def test_data_structure_validation(self):
        """Test exported data structure validation"""
        print("\n🏗️ Testing Data Structure Validation...")
        
        try:
            # Get export data
            export_response = self.session.get(f"{BACKEND_URL}/data-management/export-all")
            
            if export_response.status_code == 200:
                export_data = export_response.json()
                
                # Validate export structure
                required_top_level = ["export_timestamp", "system_version", "data"]
                structure_valid = all(field in export_data for field in required_top_level)
                
                if structure_valid:
                    self.log_test("Export data structure validation", True, "All required top-level fields present")
                    
                    # Check data types in export
                    data_section = export_data.get("data", {})
                    expected_data_types = ["raw_materials", "invoices", "treasury_transactions", "work_orders", "pricing"]
                    
                    found_types = []
                    for data_type in expected_data_types:
                        if data_type in data_section:
                            found_types.append(data_type)
                    
                    if len(found_types) >= 3:  # At least 3 data types should be present
                        self.log_test("Export data types validation", True, f"Found {len(found_types)} data types: {', '.join(found_types)}")
                    else:
                        self.log_test("Export data types validation", False, f"Only found {len(found_types)} data types")
                        
                else:
                    missing = [field for field in required_top_level if field not in export_data]
                    self.log_test("Export data structure validation", False, f"Missing fields: {missing}")
            else:
                self.log_test("Export data structure validation", False, f"HTTP {export_response.status_code}")
                
        except Exception as e:
            self.log_test("Export data structure validation", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Backend API Testing for Master Seal System - Review Focus")
        print("=" * 70)
        
        # Test 1: Payment Method Change Fix
        self.test_payment_method_change_fix()
        
        # Test 2: Data Management APIs
        self.test_data_management_apis()
        
        # Test 3: Error Handling and Arabic Messages
        self.test_error_handling_and_arabic_messages()
        
        # Test 4: Data Structure Validation
        self.test_data_structure_validation()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: All major functionality working!")
        elif success_rate >= 75:
            print("✅ GOOD: Most functionality working with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some functionality working, needs attention")
        else:
            print("❌ CRITICAL: Major issues found, immediate attention required")
        
        # Print failed tests details
        failed_tests = [test for test in self.test_results if not test["passed"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = ReviewFocusedTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Testing completed with failures!")
        sys.exit(1)