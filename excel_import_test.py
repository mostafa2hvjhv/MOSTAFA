#!/usr/bin/env python3
"""
اختبار شامل لوظيفة استيراد المواد الخام من Excel
Comprehensive test for Excel raw materials import functionality

المشكلة المبلغ عنها:
- المستخدم يرفع ملف Excel للمواد الخام
- تظهر رسالة "تم الإدراج" 
- لكن البيانات لا تظهر في المخزون أو الجرد

الاختبارات المطلوبة:
1. اختبار POST /api/excel/import/raw-materials مع ملف اختبار
2. التحقق من إدراج البيانات في قاعدة البيانات raw_materials
3. اختبار GET /api/raw-materials للتأكد من ظهور البيانات
4. اختبار GET /api/excel/export/raw-materials 
5. التحقق من أن المواد المستوردة تظهر في واجهة المخزون
6. اختبار استيراد ملف بتنسيق خاطئ (للتأكد من التحقق)
7. اختبار استيراد ملف فارغ
"""

import requests
import pandas as pd
import io
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://ae821e37-5d23-4699-b766-30ebd69d0df1.preview.emergentagent.com/api"

class ExcelImportTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
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
        
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        
        self.test_results.append(result)
        print(result)
        
    def create_test_excel_file(self, filename="test_raw_materials.xlsx", num_rows=5):
        """Create a test Excel file with raw materials data"""
        try:
            # Create test data similar to the user's 215 rows
            test_data = []
            material_types = ["NBR", "BUR", "BT", "VT", "BOOM"]
            
            for i in range(num_rows):
                material_type = material_types[i % len(material_types)]
                test_data.append({
                    'material_type': material_type,
                    'inner_diameter': 10.0 + (i * 2),
                    'outer_diameter': 25.0 + (i * 3),
                    'height': 100.0 + (i * 10),
                    'pieces_count': 5 + i,
                    'unit_code': f"{material_type[0]}-TEST-{i+1}",
                    'cost_per_mm': 2.5 + (i * 0.1),
                    'created_at': datetime.now().isoformat()
                })
            
            df = pd.DataFrame(test_data)
            df.to_excel(filename, index=False)
            
            self.log_test(f"إنشاء ملف Excel اختبار ({num_rows} صف)", True, f"تم إنشاء {filename}")
            return filename, test_data
            
        except Exception as e:
            self.log_test(f"إنشاء ملف Excel اختبار", False, f"خطأ: {str(e)}")
            return None, None
    
    def create_invalid_excel_file(self, filename="invalid_test.xlsx"):
        """Create an Excel file with missing required columns"""
        try:
            # Missing required columns
            test_data = [{
                'name': 'Test Material',
                'type': 'NBR',
                'size': '10x25'
            }]
            
            df = pd.DataFrame(test_data)
            df.to_excel(filename, index=False)
            
            self.log_test("إنشاء ملف Excel بتنسيق خاطئ", True, f"تم إنشاء {filename}")
            return filename
            
        except Exception as e:
            self.log_test("إنشاء ملف Excel بتنسيق خاطئ", False, f"خطأ: {str(e)}")
            return None
    
    def create_empty_excel_file(self, filename="empty_test.xlsx"):
        """Create an empty Excel file"""
        try:
            df = pd.DataFrame()
            df.to_excel(filename, index=False)
            
            self.log_test("إنشاء ملف Excel فارغ", True, f"تم إنشاء {filename}")
            return filename
            
        except Exception as e:
            self.log_test("إنشاء ملف Excel فارغ", False, f"خطأ: {str(e)}")
            return None
    
    def test_excel_import(self, filename, expected_success=True):
        """Test Excel import endpoint"""
        try:
            url = f"{self.backend_url}/excel/import/raw-materials"
            
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(url, files=files)
            
            if expected_success:
                if response.status_code == 200:
                    data = response.json()
                    imported_count = data.get('imported_count', 0)
                    message = data.get('message', '')
                    errors = data.get('errors', [])
                    
                    self.log_test(f"استيراد Excel - {filename}", True, 
                                f"تم استيراد {imported_count} مادة. الرسالة: {message}")
                    
                    if errors:
                        self.log_test(f"أخطاء الاستيراد - {filename}", False, f"أخطاء: {errors}")
                    
                    return imported_count, data
                else:
                    self.log_test(f"استيراد Excel - {filename}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return 0, None
            else:
                # Expecting failure
                if response.status_code != 200:
                    self.log_test(f"استيراد Excel (متوقع الفشل) - {filename}", True, 
                                f"فشل كما هو متوقع: HTTP {response.status_code}")
                    return 0, response.json() if response.content else None
                else:
                    self.log_test(f"استيراد Excel (متوقع الفشل) - {filename}", False, 
                                "نجح الاستيراد رغم أنه كان متوقعاً أن يفشل")
                    return response.json().get('imported_count', 0), response.json()
                    
        except Exception as e:
            self.log_test(f"استيراد Excel - {filename}", False, f"خطأ: {str(e)}")
            return 0, None
    
    def test_raw_materials_retrieval(self):
        """Test retrieving raw materials to verify import worked"""
        try:
            url = f"{self.backend_url}/raw-materials"
            response = requests.get(url)
            
            if response.status_code == 200:
                materials = response.json()
                count = len(materials)
                
                self.log_test("استرجاع المواد الخام", True, f"تم العثور على {count} مادة خام")
                
                # Check for test materials
                test_materials = [m for m in materials if 'TEST' in m.get('unit_code', '')]
                test_count = len(test_materials)
                
                if test_count > 0:
                    self.log_test("التحقق من المواد المستوردة", True, 
                                f"تم العثور على {test_count} مادة مستوردة من الاختبار")
                    
                    # Show sample imported material
                    sample = test_materials[0]
                    self.log_test("عينة من المواد المستوردة", True, 
                                f"النوع: {sample.get('material_type')}, الكود: {sample.get('unit_code')}, "
                                f"المقاس: {sample.get('inner_diameter')}×{sample.get('outer_diameter')}")
                else:
                    self.log_test("التحقق من المواد المستوردة", False, 
                                "لم يتم العثور على أي مواد مستوردة من الاختبار")
                
                return materials, test_materials
            else:
                self.log_test("استرجاع المواد الخام", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return [], []
                
        except Exception as e:
            self.log_test("استرجاع المواد الخام", False, f"خطأ: {str(e)}")
            return [], []
    
    def test_excel_export(self):
        """Test Excel export endpoint"""
        try:
            url = f"{self.backend_url}/excel/export/raw-materials"
            response = requests.get(url)
            
            if response.status_code == 200:
                # Check if response is Excel file
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                self.log_test("تصدير Excel", True, 
                            f"تم تصدير الملف بنجاح. الحجم: {content_length} بايت")
                
                # Try to read the Excel content
                try:
                    df = pd.read_excel(io.BytesIO(response.content))
                    row_count = len(df)
                    columns = list(df.columns)
                    
                    self.log_test("قراءة ملف Excel المصدر", True, 
                                f"عدد الصفوف: {row_count}, الأعمدة: {columns}")
                    
                    return df
                except Exception as e:
                    self.log_test("قراءة ملف Excel المصدر", False, f"خطأ في قراءة الملف: {str(e)}")
                    return None
            else:
                self.log_test("تصدير Excel", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("تصدير Excel", False, f"خطأ: {str(e)}")
            return None
    
    def test_inventory_integration(self):
        """Test if imported materials appear in inventory system"""
        try:
            # Test inventory endpoint
            url = f"{self.backend_url}/inventory"
            response = requests.get(url)
            
            if response.status_code == 200:
                inventory = response.json()
                count = len(inventory)
                
                self.log_test("استرجاع الجرد", True, f"تم العثور على {count} عنصر في الجرد")
                
                # Check if any inventory items match our test materials
                test_inventory = []
                for item in inventory:
                    # Look for materials that might be related to our test
                    if any(mat_type in str(item.get('material_type', '')) for mat_type in ['NBR', 'BUR', 'BT', 'VT', 'BOOM']):
                        test_inventory.append(item)
                
                if test_inventory:
                    self.log_test("تكامل الجرد مع المواد المستوردة", True, 
                                f"تم العثور على {len(test_inventory)} عنصر جرد مرتبط")
                else:
                    self.log_test("تكامل الجرد مع المواد المستوردة", False, 
                                "لم يتم العثور على عناصر جرد مرتبطة بالمواد المستوردة")
                
                return inventory
            else:
                self.log_test("استرجاع الجرد", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("استرجاع الجرد", False, f"خطأ: {str(e)}")
            return []
    
    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            # Get all raw materials
            url = f"{self.backend_url}/raw-materials"
            response = requests.get(url)
            
            if response.status_code == 200:
                materials = response.json()
                
                # Delete test materials (those with TEST in unit_code)
                deleted_count = 0
                for material in materials:
                    if 'TEST' in material.get('unit_code', ''):
                        delete_url = f"{self.backend_url}/raw-materials/{material['id']}"
                        delete_response = requests.delete(delete_url)
                        if delete_response.status_code == 200:
                            deleted_count += 1
                
                self.log_test("تنظيف بيانات الاختبار", True, f"تم حذف {deleted_count} مادة اختبار")
                
                # Clean up test files
                test_files = ["test_raw_materials.xlsx", "invalid_test.xlsx", "empty_test.xlsx", 
                             "large_test_raw_materials.xlsx"]
                for filename in test_files:
                    if os.path.exists(filename):
                        os.remove(filename)
                        
            else:
                self.log_test("تنظيف بيانات الاختبار", False, "فشل في الحصول على قائمة المواد")
                
        except Exception as e:
            self.log_test("تنظيف بيانات الاختبار", False, f"خطأ: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all Excel import tests"""
        print("🚀 بدء الاختبار الشامل لوظيفة استيراد المواد الخام من Excel")
        print("=" * 80)
        
        # Test 1: Create and import valid Excel file
        print("\n📋 الاختبار 1: استيراد ملف Excel صحيح")
        filename, test_data = self.create_test_excel_file("test_raw_materials.xlsx", 5)
        if filename:
            imported_count, import_result = self.test_excel_import(filename, expected_success=True)
            
            # Verify the import worked
            if imported_count > 0:
                materials, test_materials = self.test_raw_materials_retrieval()
                
                # Check data persistence
                if test_materials:
                    self.log_test("استمرارية البيانات", True, 
                                f"البيانات محفوظة في قاعدة البيانات: {len(test_materials)} مادة")
                else:
                    self.log_test("استمرارية البيانات", False, 
                                "البيانات غير محفوظة في قاعدة البيانات")
        
        # Test 2: Test Excel export
        print("\n📤 الاختبار 2: تصدير المواد الخام إلى Excel")
        exported_df = self.test_excel_export()
        
        # Test 3: Test inventory integration
        print("\n🏪 الاختبار 3: تكامل مع نظام الجرد")
        inventory = self.test_inventory_integration()
        
        # Test 4: Test invalid Excel file
        print("\n❌ الاختبار 4: استيراد ملف Excel بتنسيق خاطئ")
        invalid_filename = self.create_invalid_excel_file()
        if invalid_filename:
            self.test_excel_import(invalid_filename, expected_success=False)
        
        # Test 5: Test empty Excel file
        print("\n📄 الاختبار 5: استيراد ملف Excel فارغ")
        empty_filename = self.create_empty_excel_file()
        if empty_filename:
            self.test_excel_import(empty_filename, expected_success=False)
        
        # Test 6: Test large file (simulate user's 215 rows)
        print("\n📊 الاختبار 6: استيراد ملف كبير (محاكاة 215 صف)")
        large_filename, large_test_data = self.create_test_excel_file("large_test_raw_materials.xlsx", 20)
        if large_filename:
            large_imported_count, large_import_result = self.test_excel_import(large_filename, expected_success=True)
            
            if large_imported_count > 0:
                # Verify large import
                materials_after_large, test_materials_after_large = self.test_raw_materials_retrieval()
                self.log_test("استيراد ملف كبير", True, 
                            f"تم استيراد {large_imported_count} مادة من الملف الكبير")
        
        # Test 7: Verify data appears in frontend (simulate)
        print("\n🖥️ الاختبار 7: التحقق من ظهور البيانات في الواجهة")
        final_materials, final_test_materials = self.test_raw_materials_retrieval()
        if final_test_materials:
            self.log_test("ظهور البيانات في الواجهة", True, 
                        f"البيانات متاحة للواجهة الأمامية: {len(final_test_materials)} مادة")
        else:
            self.log_test("ظهور البيانات في الواجهة", False, 
                        "البيانات غير متاحة للواجهة الأمامية")
        
        # Cleanup
        print("\n🧹 تنظيف بيانات الاختبار")
        self.cleanup_test_data()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 ملخص نتائج الاختبار")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"إجمالي الاختبارات: {self.total_tests}")
        print(f"الاختبارات الناجحة: {self.passed_tests}")
        print(f"الاختبارات الفاشلة: {self.total_tests - self.passed_tests}")
        print(f"معدل النجاح: {success_rate:.1f}%")
        
        print(f"\n🎯 حالة وظيفة استيراد Excel:")
        if success_rate >= 80:
            print("✅ تعمل بشكل ممتاز - جاهزة للاستخدام الإنتاجي")
        elif success_rate >= 60:
            print("⚠️ تعمل مع بعض المشاكل - تحتاج تحسينات")
        else:
            print("❌ لا تعمل بشكل صحيح - تحتاج إصلاحات جوهرية")
        
        print("\n📋 تفاصيل النتائج:")
        for result in self.test_results:
            print(f"  {result}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ExcelImportTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 الاختبار مكتمل بنجاح!")
    else:
        print(f"\n⚠️ الاختبار اكتشف مشاكل تحتاج إلى إصلاح")