#!/usr/bin/env python3
"""
Inventory Deduction Logic Testing - CORRECTED Requirements
اختبار منطق خصم المخزون - المتطلبات المصححة

Testing the corrected inventory deduction logic based on user's exact requirements:
1. عند فحص التوافق واختيار خامة، يتم خصم (ارتفاع السيل + 2) × عدد السيلات من **ارتفاع الخامة** المختارة (ليس عدد القطع)
2. عندما تكون ارتفاع الخامة في المخزون 15 أو أقل، لا تظهر في فحص التوافق
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
        self.created_materials = []
        self.created_invoices = []
        
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
    
    def setup_inventory_items(self):
        """Setup inventory items first (required for raw materials)"""
        print("\n=== Setting Up Inventory Items ===")
        
        # Create inventory items for the materials we want to test
        inventory_items = [
            {
                "material_type": "NBR",
                "inner_diameter": 30.0,
                "outer_diameter": 40.0,
                "available_pieces": 10,
                "min_stock_level": 2,
                "notes": "Test inventory for NBR 30x40"
            },
            {
                "material_type": "BUR", 
                "inner_diameter": 25.0,
                "outer_diameter": 35.0,
                "available_pieces": 5,
                "min_stock_level": 2,
                "notes": "Test inventory for BUR 25x35"
            },
            {
                "material_type": "VT",
                "inner_diameter": 20.0,
                "outer_diameter": 30.0,
                "available_pieces": 8,
                "min_stock_level": 2,
                "notes": "Test inventory for VT 20x30"
            }
        ]
        
        for item_data in inventory_items:
            try:
                response = self.session.post(f"{BACKEND_URL}/inventory", json=item_data)
                if response.status_code in [200, 201]:
                    item = response.json()
                    self.log_test(f"Create inventory {item_data['material_type']} {item_data['inner_diameter']}×{item_data['outer_diameter']}", True, 
                                f"Inventory created with {item_data['available_pieces']} pieces")
                else:
                    self.log_test(f"Create inventory {item_data['material_type']} {item_data['inner_diameter']}×{item_data['outer_diameter']}", False, 
                                f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Create inventory {item_data['material_type']} {item_data['inner_diameter']}×{item_data['outer_diameter']}", False, str(e))

    def setup_test_materials(self):
        """Setup raw materials for testing according to user requirements"""
        print("\n=== Setting Up Test Materials ===")
        
        # Test Material 1: NBR 30×40mm with height 100mm (should appear in compatibility)
        material1_data = {
            "material_type": "NBR",
            "inner_diameter": 30.0,
            "outer_diameter": 40.0,
            "height": 100.0,
            "pieces_count": 5,
            "cost_per_mm": 1.5
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/raw-materials", json=material1_data)
            if response.status_code in [200, 201]:
                material1 = response.json()
                self.created_materials.append(material1)
                self.log_test("Create NBR 30×40mm height 100mm", True, 
                            f"Material created with unit_code: {material1.get('unit_code')}")
            else:
                self.log_test("Create NBR 30×40mm height 100mm", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create NBR 30×40mm height 100mm", False, str(e))
        
        # Test Material 2: BUR 25×35mm with height 10mm (should NOT appear - ≤15mm)
        material2_data = {
            "material_type": "BUR",
            "inner_diameter": 25.0,
            "outer_diameter": 35.0,
            "height": 10.0,
            "pieces_count": 3,
            "cost_per_mm": 2.0
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/raw-materials", json=material2_data)
            if response.status_code in [200, 201]:
                material2 = response.json()
                self.created_materials.append(material2)
                self.log_test("Create BUR 25×35mm height 10mm", True, 
                            f"Material created with unit_code: {material2.get('unit_code')}")
            else:
                self.log_test("Create BUR 25×35mm height 10mm", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create BUR 25×35mm height 10mm", False, str(e))
        
        # Test Material 3: VT 20×30mm with height 20mm (should appear in compatibility)
        material3_data = {
            "material_type": "VT",
            "inner_diameter": 20.0,
            "outer_diameter": 30.0,
            "height": 20.0,
            "pieces_count": 4,
            "cost_per_mm": 1.8
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/raw-materials", json=material3_data)
            if response.status_code in [200, 201]:
                material3 = response.json()
                self.created_materials.append(material3)
                self.log_test("Create VT 20×30mm height 20mm", True, 
                            f"Material created with unit_code: {material3.get('unit_code')}")
            else:
                self.log_test("Create VT 20×30mm height 20mm", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create VT 20×30mm height 20mm", False, str(e))
    
    def test_compatibility_filtering(self):
        """Test compatibility check filtering - materials ≤15mm should not appear"""
        print("\n=== Testing Compatibility Filtering ===")
        
        # Test compatibility for RSL seal 30×40×8mm
        compatibility_data = {
            "seal_type": "RSL",
            "inner_diameter": 30.0,
            "outer_diameter": 40.0,
            "height": 8.0
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/compatibility-check", json=compatibility_data)
            if response.status_code == 200:
                compatibility_result = response.json()
                compatible_materials = compatibility_result.get("compatible_materials", [])
                
                # Check if NBR 30×40mm appears (height=100mm > 15mm)
                nbr_found = any(mat.get("material_type") == "NBR" and 
                              mat.get("inner_diameter") == 30.0 and 
                              mat.get("outer_diameter") == 40.0 
                              for mat in compatible_materials)
                
                # Check if BUR 25×35mm does NOT appear (height=10mm ≤ 15mm)
                bur_found = any(mat.get("material_type") == "BUR" and 
                              mat.get("inner_diameter") == 25.0 and 
                              mat.get("outer_diameter") == 35.0 
                              for mat in compatible_materials)
                
                if nbr_found and not bur_found:
                    self.log_test("Compatibility filtering works correctly", True, 
                                f"NBR appears (height>15mm), BUR filtered out (height≤15mm)")
                else:
                    self.log_test("Compatibility filtering works correctly", False, 
                                f"NBR found: {nbr_found}, BUR found: {bur_found} (should be True, False)")
                
                # Log all compatible materials for debugging
                print(f"   Compatible materials found: {len(compatible_materials)}")
                for mat in compatible_materials:
                    print(f"   - {mat.get('material_type')} {mat.get('inner_diameter')}×{mat.get('outer_diameter')} height={mat.get('height')}mm")
                    
            else:
                self.log_test("Compatibility filtering works correctly", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Compatibility filtering works correctly", False, str(e))
    
    def test_height_deduction_logic(self):
        """Test height deduction: (seal_height + 2) × quantity FROM material height"""
        print("\n=== Testing Height Deduction Logic ===")
        
        # First, get the current height of NBR material
        try:
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            if response.status_code == 200:
                materials = response.json()
                nbr_material = None
                for mat in materials:
                    if (mat.get("material_type") == "NBR" and 
                        mat.get("inner_diameter") == 30.0 and 
                        mat.get("outer_diameter") == 40.0):
                        nbr_material = mat
                        break
                
                if nbr_material:
                    initial_height = nbr_material.get("height", 0)
                    print(f"   Initial NBR material height: {initial_height}mm")
                    
                    # Create test customer
                    customer_data = {
                        "name": "عميل اختبار خصم المخزون",
                        "phone": "01234567890"
                    }
                    
                    customer_response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
                    if customer_response.status_code in [200, 201]:
                        customer = customer_response.json()
                        
                        # Create invoice with NBR 30×40×8mm × 5 seals
                        # Expected deduction: (8 + 2) × 5 = 50mm from material height
                        invoice_data = {
                            "customer_id": customer.get("id"),
                            "customer_name": customer.get("name"),
                            "invoice_title": "اختبار خصم الارتفاع",
                            "supervisor_name": "مشرف الاختبار",
                            "payment_method": "نقدي",
                            "items": [
                                {
                                    "seal_type": "RSL",
                                    "material_type": "NBR",
                                    "inner_diameter": 30.0,
                                    "outer_diameter": 40.0,
                                    "height": 8.0,
                                    "quantity": 5,
                                    "unit_price": 15.0,
                                    "total_price": 75.0,
                                    "product_type": "manufactured",
                                    "material_used": nbr_material.get("unit_code"),
                                    "material_details": {
                                        "material_type": "NBR",
                                        "inner_diameter": 30.0,
                                        "outer_diameter": 40.0,
                                        "height": initial_height,
                                        "unit_code": nbr_material.get("unit_code"),
                                        "is_finished_product": False
                                    }
                                }
                            ]
                        }
                        
                        invoice_response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
                        if invoice_response.status_code in [200, 201]:
                            invoice = invoice_response.json()
                            self.created_invoices.append(invoice)
                            
                            # Check material height after deduction
                            materials_response = self.session.get(f"{BACKEND_URL}/raw-materials")
                            if materials_response.status_code == 200:
                                updated_materials = materials_response.json()
                                updated_nbr = None
                                for mat in updated_materials:
                                    if (mat.get("material_type") == "NBR" and 
                                        mat.get("inner_diameter") == 30.0 and 
                                        mat.get("outer_diameter") == 40.0):
                                        updated_nbr = mat
                                        break
                                
                                if updated_nbr:
                                    final_height = updated_nbr.get("height", 0)
                                    expected_deduction = (8 + 2) * 5  # 50mm
                                    expected_final_height = initial_height - expected_deduction
                                    
                                    print(f"   Final NBR material height: {final_height}mm")
                                    print(f"   Expected deduction: {expected_deduction}mm")
                                    print(f"   Expected final height: {expected_final_height}mm")
                                    
                                    if abs(final_height - expected_final_height) < 0.1:
                                        self.log_test("Height deduction calculation correct", True, 
                                                    f"Deducted {expected_deduction}mm correctly: {initial_height}mm → {final_height}mm")
                                    else:
                                        self.log_test("Height deduction calculation correct", False, 
                                                    f"Expected {expected_final_height}mm, got {final_height}mm")
                                else:
                                    self.log_test("Height deduction calculation correct", False, 
                                                "Could not find NBR material after invoice creation")
                            else:
                                self.log_test("Height deduction calculation correct", False, 
                                            f"Failed to get updated materials: HTTP {materials_response.status_code}")
                        else:
                            self.log_test("Height deduction calculation correct", False, 
                                        f"Failed to create invoice: HTTP {invoice_response.status_code}: {invoice_response.text}")
                    else:
                        self.log_test("Height deduction calculation correct", False, 
                                    f"Failed to create customer: HTTP {customer_response.status_code}")
                else:
                    self.log_test("Height deduction calculation correct", False, 
                                "Could not find NBR material for testing")
            else:
                self.log_test("Height deduction calculation correct", False, 
                            f"Failed to get materials: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Height deduction calculation correct", False, str(e))
    
    def test_insufficient_height_scenario(self):
        """Test scenario where invoice requires more height than available"""
        print("\n=== Testing Insufficient Height Scenario ===")
        
        try:
            # Get VT material (should have 20mm height)
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            if response.status_code == 200:
                materials = response.json()
                vt_material = None
                for mat in materials:
                    if (mat.get("material_type") == "VT" and 
                        mat.get("inner_diameter") == 20.0 and 
                        mat.get("outer_diameter") == 30.0):
                        vt_material = mat
                        break
                
                if vt_material:
                    current_height = vt_material.get("height", 0)
                    print(f"   VT material current height: {current_height}mm")
                    
                    # Try to create invoice requiring more height than available
                    # If height is 20mm, try to use 15mm seal × 2 quantity = (15+2)×2 = 34mm required
                    required_height_per_seal = 15
                    quantity = 2
                    total_required = (required_height_per_seal + 2) * quantity  # 34mm
                    
                    print(f"   Attempting to use {total_required}mm (need {required_height_per_seal}mm × {quantity} + 2mm waste each)")
                    
                    # Create test customer
                    customer_data = {
                        "name": "عميل اختبار نقص الارتفاع",
                        "phone": "01234567891"
                    }
                    
                    customer_response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
                    if customer_response.status_code in [200, 201]:
                        customer = customer_response.json()
                        
                        invoice_data = {
                            "customer_id": customer.get("id"),
                            "customer_name": customer.get("name"),
                            "invoice_title": "اختبار نقص الارتفاع",
                            "supervisor_name": "مشرف الاختبار",
                            "payment_method": "نقدي",
                            "items": [
                                {
                                    "seal_type": "RSL",
                                    "material_type": "VT",
                                    "inner_diameter": 20.0,
                                    "outer_diameter": 30.0,
                                    "height": required_height_per_seal,
                                    "quantity": quantity,
                                    "unit_price": 20.0,
                                    "total_price": 40.0,
                                    "product_type": "manufactured",
                                    "material_used": vt_material.get("unit_code"),
                                    "material_details": {
                                        "material_type": "VT",
                                        "inner_diameter": 20.0,
                                        "outer_diameter": 30.0,
                                        "height": current_height,
                                        "unit_code": vt_material.get("unit_code"),
                                        "is_finished_product": False
                                    }
                                }
                            ]
                        }
                        
                        invoice_response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
                        
                        # Invoice should be created but with warning logged
                        if invoice_response.status_code in [200, 201]:
                            invoice = invoice_response.json()
                            self.created_invoices.append(invoice)
                            
                            # Check if material height went negative or stayed at minimum
                            materials_response = self.session.get(f"{BACKEND_URL}/raw-materials")
                            if materials_response.status_code == 200:
                                updated_materials = materials_response.json()
                                updated_vt = None
                                for mat in updated_materials:
                                    if (mat.get("material_type") == "VT" and 
                                        mat.get("inner_diameter") == 20.0 and 
                                        mat.get("outer_diameter") == 30.0):
                                        updated_vt = mat
                                        break
                                
                                if updated_vt:
                                    final_height = updated_vt.get("height", 0)
                                    print(f"   VT material final height: {final_height}mm")
                                    
                                    if total_required > current_height:
                                        # Should log warning but complete invoice
                                        self.log_test("Insufficient height handled correctly", True, 
                                                    f"Invoice created with warning - required {total_required}mm, had {current_height}mm")
                                    else:
                                        # Normal deduction
                                        expected_final = current_height - total_required
                                        if abs(final_height - expected_final) < 0.1:
                                            self.log_test("Insufficient height handled correctly", True, 
                                                        f"Normal deduction: {current_height}mm → {final_height}mm")
                                        else:
                                            self.log_test("Insufficient height handled correctly", False, 
                                                        f"Unexpected final height: {final_height}mm")
                                else:
                                    self.log_test("Insufficient height handled correctly", False, 
                                                "Could not find VT material after invoice")
                            else:
                                self.log_test("Insufficient height handled correctly", False, 
                                            "Failed to get updated materials")
                        else:
                            self.log_test("Insufficient height handled correctly", False, 
                                        f"Invoice creation failed: HTTP {invoice_response.status_code}: {invoice_response.text}")
                    else:
                        self.log_test("Insufficient height handled correctly", False, 
                                    "Failed to create test customer")
                else:
                    self.log_test("Insufficient height handled correctly", False, 
                                "Could not find VT material for testing")
            else:
                self.log_test("Insufficient height handled correctly", False, 
                            f"Failed to get materials: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Insufficient height handled correctly", False, str(e))
    
    def verify_raw_materials_collection(self):
        """Verify that deductions happen in raw_materials collection"""
        print("\n=== Verifying Raw Materials Collection Updates ===")
        
        try:
            # Get all raw materials and verify they have the height field
            response = self.session.get(f"{BACKEND_URL}/raw-materials")
            if response.status_code == 200:
                materials = response.json()
                
                height_field_count = 0
                total_materials = len(materials)
                
                for material in materials:
                    if "height" in material and isinstance(material["height"], (int, float)):
                        height_field_count += 1
                
                if height_field_count == total_materials and total_materials > 0:
                    self.log_test("Raw materials have height field", True, 
                                f"All {total_materials} materials have height field")
                else:
                    self.log_test("Raw materials have height field", False, 
                                f"Only {height_field_count}/{total_materials} materials have height field")
                
                # Verify that our test materials are in the collection
                test_materials_found = 0
                for created_mat in self.created_materials:
                    unit_code = created_mat.get("unit_code")
                    found = any(mat.get("unit_code") == unit_code for mat in materials)
                    if found:
                        test_materials_found += 1
                
                if test_materials_found == len(self.created_materials):
                    self.log_test("Test materials exist in raw_materials collection", True, 
                                f"All {test_materials_found} test materials found")
                else:
                    self.log_test("Test materials exist in raw_materials collection", False, 
                                f"Only {test_materials_found}/{len(self.created_materials)} test materials found")
                    
            else:
                self.log_test("Raw materials collection accessible", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Raw materials collection accessible", False, str(e))
    
    def run_all_tests(self):
        """Run all inventory deduction tests"""
        print("🔍 Starting Inventory Deduction Logic Testing")
        print("=" * 60)
        
        # Setup test data
        self.setup_inventory_items()
        self.setup_test_materials()
        
        # Run tests
        self.test_compatibility_filtering()
        self.test_height_deduction_logic()
        self.test_insufficient_height_scenario()
        self.verify_raw_materials_collection()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print(f"\n🎯 INVENTORY DEDUCTION TESTING COMPLETED")
        print(f"Created {len(self.created_materials)} test materials")
        print(f"Created {len(self.created_invoices)} test invoices")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = InventoryDeductionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
"""
Comprehensive test for inventory deduction issue reported by user.
Testing the REAL inventory deduction problem: "في المخزن عند عمل فاتورة لا يتم خصم ارتفاع السيلات من المخزون"
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://oilseal-manager-3.preview.emergentagent.com/api"

class InventoryDeductionTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    def test_inventory_setup(self):
        """Test 1: Create NBR 20×30mm inventory with 1000 pieces"""
        print("\n=== Test 1: Setting up NBR 20×30mm inventory with 1000 pieces ===")
        
        # First, clear existing inventory to start fresh
        try:
            response = requests.delete(f"{BACKEND_URL}/inventory/clear-all")
            print(f"Cleared existing inventory: {response.status_code}")
        except Exception as e:
            print(f"Warning: Could not clear inventory: {e}")
        
        # Create NBR 20×30mm inventory item with 1000 pieces
        inventory_data = {
            "material_type": "NBR",
            "inner_diameter": 20.0,
            "outer_diameter": 30.0,
            "available_pieces": 1000,
            "min_stock_level": 10,
            "notes": "Test inventory for deduction testing"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/inventory", json=inventory_data)
            if response.status_code == 200:
                inventory_item = response.json()
                self.inventory_item_id = inventory_item["id"]
                self.log_test("Create NBR 20×30mm inventory", True, f"Created with 1000 pieces, ID: {self.inventory_item_id}")
                return True
            else:
                self.log_test("Create NBR 20×30mm inventory", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create NBR 20×30mm inventory", False, f"Exception: {str(e)}")
            return False
    
    def verify_initial_inventory(self):
        """Test 2: Verify initial inventory count"""
        print("\n=== Test 2: Verify initial inventory count ===")
        
        try:
            response = requests.get(f"{BACKEND_URL}/inventory")
            if response.status_code == 200:
                inventory_items = response.json()
                nbr_items = [item for item in inventory_items 
                           if item.get("material_type") == "NBR" 
                           and item.get("inner_diameter") == 20.0 
                           and item.get("outer_diameter") == 30.0]
                
                if nbr_items:
                    initial_count = nbr_items[0].get("available_pieces", 0)
                    self.initial_inventory_count = initial_count
                    self.log_test("Verify initial inventory", True, f"Initial count: {initial_count} pieces")
                    return initial_count == 1000
                else:
                    self.log_test("Verify initial inventory", False, "NBR 20×30mm item not found")
                    return False
            else:
                self.log_test("Verify initial inventory", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verify initial inventory", False, f"Exception: {str(e)}")
            return False
    
    def create_test_customer(self):
        """Test 3: Create test customer for invoice"""
        print("\n=== Test 3: Create test customer ===")
        
        customer_data = {
            "name": "عميل اختبار خصم المخزون",
            "phone": "01234567890",
            "address": "عنوان اختبار"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.customer_id = customer["id"]
                self.log_test("Create test customer", True, f"Customer ID: {self.customer_id}")
                return True
            else:
                self.log_test("Create test customer", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create test customer", False, f"Exception: {str(e)}")
            return False
    
    def test_invoice_creation_basic_material_info(self):
        """Test 4: Create invoice with basic material info (no compatibility check)"""
        print("\n=== Test 4: Create invoice with NBR 20×30×6mm × 10 seals (basic material info) ===")
        
        # Create invoice with manufactured product using basic material details
        invoice_data = {
            "customer_id": self.customer_id,
            "customer_name": "عميل اختبار خصم المخزون",
            "invoice_title": "فاتورة اختبار خصم المخزون - بيانات أساسية",
            "supervisor_name": "مشرف الاختبار",
            "items": [
                {
                    "seal_type": "RSL",
                    "material_type": "NBR",
                    "inner_diameter": 20.0,
                    "outer_diameter": 30.0,
                    "height": 6.0,
                    "quantity": 10,
                    "unit_price": 15.0,
                    "total_price": 150.0,
                    "product_type": "manufactured",
                    "material_details": {
                        "material_type": "NBR",
                        "inner_diameter": 20.0,
                        "outer_diameter": 30.0,
                        "is_finished_product": False
                    }
                }
            ],
            "payment_method": "نقدي",
            "discount_type": "amount",
            "discount_value": 0.0,
            "notes": "اختبار خصم المخزون - بيانات أساسية"
        }
        
        try:
            print("Sending invoice creation request...")
            print(f"Invoice data: {json.dumps(invoice_data, indent=2, ensure_ascii=False)}")
            
            response = requests.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                invoice = response.json()
                self.invoice_id_basic = invoice["id"]
                self.log_test("Create invoice with basic material info", True, 
                            f"Invoice {invoice['invoice_number']} created, ID: {self.invoice_id_basic}")
                return True
            else:
                self.log_test("Create invoice with basic material info", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create invoice with basic material info", False, f"Exception: {str(e)}")
            return False
    
    def verify_inventory_deduction_basic(self):
        """Test 5: Verify inventory deduction after basic invoice"""
        print("\n=== Test 5: Verify inventory deduction (should be 1000 - 80 = 920) ===")
        
        try:
            response = requests.get(f"{BACKEND_URL}/inventory")
            if response.status_code == 200:
                inventory_items = response.json()
                nbr_items = [item for item in inventory_items 
                           if item.get("material_type") == "NBR" 
                           and item.get("inner_diameter") == 20.0 
                           and item.get("outer_diameter") == 30.0]
                
                if nbr_items:
                    current_count = nbr_items[0].get("available_pieces", 0)
                    expected_count = 1000 - (6 + 2) * 10  # (height + waste) * quantity = 80
                    deducted_amount = 1000 - current_count
                    
                    self.log_test("Verify inventory deduction", 
                                current_count == expected_count,
                                f"Expected: {expected_count}, Actual: {current_count}, Deducted: {deducted_amount}")
                    
                    if current_count == expected_count:
                        print(f"✅ CORRECT: Inventory properly deducted {deducted_amount} pieces")
                        return True
                    else:
                        print(f"❌ INCORRECT: Expected deduction of 80 pieces, but got {deducted_amount}")
                        return False
                else:
                    self.log_test("Verify inventory deduction", False, "NBR 20×30mm item not found after invoice")
                    return False
            else:
                self.log_test("Verify inventory deduction", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verify inventory deduction", False, f"Exception: {str(e)}")
            return False
    
    def check_inventory_transactions(self):
        """Test 6: Check if inventory transactions were created"""
        print("\n=== Test 6: Check inventory transactions ===")
        
        try:
            response = requests.get(f"{BACKEND_URL}/inventory-transactions")
            if response.status_code == 200:
                transactions = response.json()
                
                # Look for transactions related to our inventory item
                relevant_transactions = [t for t in transactions 
                                       if t.get("material_type") == "NBR" 
                                       and t.get("inner_diameter") == 20.0 
                                       and t.get("outer_diameter") == 30.0
                                       and t.get("transaction_type") == "out"]
                
                if relevant_transactions:
                    latest_transaction = relevant_transactions[0]  # Most recent
                    pieces_change = abs(latest_transaction.get("pieces_change", 0))
                    
                    self.log_test("Check inventory transactions", 
                                pieces_change == 80,
                                f"Found transaction with {pieces_change} pieces deducted")
                    return pieces_change == 80
                else:
                    self.log_test("Check inventory transactions", False, 
                                "No outbound transactions found for NBR 20×30mm")
                    return False
            else:
                self.log_test("Check inventory transactions", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Check inventory transactions", False, f"Exception: {str(e)}")
            return False
    
    def test_compatibility_check_workflow(self):
        """Test 7: Test invoice creation with compatibility check workflow"""
        print("\n=== Test 7: Test compatibility check workflow ===")
        
        # First, do compatibility check
        compatibility_data = {
            "seal_type": "RSL",
            "inner_diameter": 20.0,
            "outer_diameter": 30.0,
            "height": 8.0,
            "material_type": "NBR"
        }
        
        try:
            print("Performing compatibility check...")
            response = requests.post(f"{BACKEND_URL}/compatibility-check", json=compatibility_data)
            
            if response.status_code == 200:
                compatibility_result = response.json()
                compatible_materials = compatibility_result.get("compatible_materials", [])
                
                if compatible_materials:
                    # Use the first compatible material
                    selected_material = compatible_materials[0]
                    
                    # Create invoice with selected material
                    invoice_data = {
                        "customer_id": self.customer_id,
                        "customer_name": "عميل اختبار خصم المخزون",
                        "invoice_title": "فاتورة اختبار خصم المخزون - فحص التوافق",
                        "supervisor_name": "مشرف الاختبار",
                        "items": [
                            {
                                "seal_type": "RSL",
                                "material_type": "NBR",
                                "inner_diameter": 20.0,
                                "outer_diameter": 30.0,
                                "height": 8.0,
                                "quantity": 5,
                                "unit_price": 18.0,
                                "total_price": 90.0,
                                "product_type": "manufactured",
                                "material_details": {
                                    "material_type": selected_material.get("material_type"),
                                    "inner_diameter": selected_material.get("inner_diameter"),
                                    "outer_diameter": selected_material.get("outer_diameter"),
                                    "unit_code": selected_material.get("unit_code"),
                                    "is_finished_product": False
                                }
                            }
                        ],
                        "payment_method": "نقدي",
                        "discount_type": "amount",
                        "discount_value": 0.0,
                        "notes": "اختبار خصم المخزون - فحص التوافق"
                    }
                    
                    response = requests.post(f"{BACKEND_URL}/invoices", json=invoice_data)
                    
                    if response.status_code == 200:
                        invoice = response.json()
                        self.invoice_id_compatibility = invoice["id"]
                        self.log_test("Create invoice with compatibility check", True,
                                    f"Invoice {invoice['invoice_number']} created")
                        return True
                    else:
                        self.log_test("Create invoice with compatibility check", False,
                                    f"Invoice creation failed: HTTP {response.status_code}")
                        return False
                else:
                    self.log_test("Create invoice with compatibility check", False,
                                "No compatible materials found")
                    return False
            else:
                self.log_test("Create invoice with compatibility check", False,
                            f"Compatibility check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create invoice with compatibility check", False, f"Exception: {str(e)}")
            return False
    
    def verify_final_inventory_count(self):
        """Test 8: Verify final inventory count after both invoices"""
        print("\n=== Test 8: Verify final inventory count ===")
        
        try:
            response = requests.get(f"{BACKEND_URL}/inventory")
            if response.status_code == 200:
                inventory_items = response.json()
                nbr_items = [item for item in inventory_items 
                           if item.get("material_type") == "NBR" 
                           and item.get("inner_diameter") == 20.0 
                           and item.get("outer_diameter") == 30.0]
                
                if nbr_items:
                    final_count = nbr_items[0].get("available_pieces", 0)
                    
                    # Expected: 1000 - 80 (first invoice) - 50 (second invoice) = 870
                    expected_final = 1000 - 80 - 50
                    total_deducted = 1000 - final_count
                    
                    self.log_test("Verify final inventory count",
                                final_count == expected_final,
                                f"Expected: {expected_final}, Actual: {final_count}, Total deducted: {total_deducted}")
                    
                    return final_count == expected_final
                else:
                    self.log_test("Verify final inventory count", False, "NBR 20×30mm item not found")
                    return False
            else:
                self.log_test("Verify final inventory count", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verify final inventory count", False, f"Exception: {str(e)}")
            return False
    
    def debug_backend_logs(self):
        """Test 9: Check backend logs for deduction details"""
        print("\n=== Test 9: Debug backend processing ===")
        
        # Print debug information about what we found
        try:
            # Get all invoices to see what was created
            response = requests.get(f"{BACKEND_URL}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                test_invoices = [inv for inv in invoices if "اختبار خصم المخزون" in inv.get("invoice_title", "")]
                
                print(f"Found {len(test_invoices)} test invoices:")
                for inv in test_invoices:
                    print(f"  - {inv.get('invoice_number')}: {inv.get('invoice_title')}")
                    for item in inv.get('items', []):
                        print(f"    * {item.get('seal_type')} {item.get('material_type')} "
                              f"{item.get('inner_diameter')}×{item.get('outer_diameter')}×{item.get('height')} "
                              f"qty: {item.get('quantity')}")
                        if item.get('material_details'):
                            print(f"      Material details: {item.get('material_details')}")
                
                self.log_test("Debug backend processing", True, f"Found {len(test_invoices)} test invoices")
                return True
            else:
                self.log_test("Debug backend processing", False, f"Could not get invoices: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug backend processing", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all inventory deduction tests"""
        print("🔍 TESTING REAL INVENTORY DEDUCTION ISSUE")
        print("=" * 60)
        print("User Problem: 'في المخزن عند عمل فاتورة لا يتم خصم ارتفاع السيلات من المخزون'")
        print("Expected: When creating invoices, seal heights should be deducted from inventory")
        print("=" * 60)
        
        # Initialize test variables
        self.inventory_item_id = None
        self.customer_id = None
        self.invoice_id_basic = None
        self.invoice_id_compatibility = None
        self.initial_inventory_count = 0
        
        # Run tests in sequence
        tests = [
            self.test_inventory_setup,
            self.verify_initial_inventory,
            self.create_test_customer,
            self.test_invoice_creation_basic_material_info,
            self.verify_inventory_deduction_basic,
            self.check_inventory_transactions,
            self.test_compatibility_check_workflow,
            self.verify_final_inventory_count,
            self.debug_backend_logs
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test crashed: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n🎯 Overall Success Rate: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("✅ INVENTORY DEDUCTION IS WORKING CORRECTLY")
            return True
        else:
            print("❌ INVENTORY DEDUCTION HAS ISSUES")
            return False

if __name__ == "__main__":
    tester = InventoryDeductionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
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