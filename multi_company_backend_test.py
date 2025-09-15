#!/usr/bin/env python3
"""
Multi-Company System Testing - نظام الشركات المتعددة
اختبار شامل لنظام Multi-Company كما هو مطلوب في المراجعة

المراحل المطلوبة:
1. إعداد الشركات الأولية (Master Seal و Faster Seal)
2. ترحيل البيانات الحالية إلى Master Seal
3. اختبار فلترة البيانات بالشركات
4. اختبار إنشاء بيانات جديدة
5. اختبار صلاحيات المستخدمين
6. اختبار APIs إدارة الشركات
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

class MultiCompanyTester:
    def __init__(self):
        self.session = requests.Session()
        self.master_seal_id = None
        self.faster_seal_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} - {test_name}")
        if details:
            print(f"   التفاصيل: {details}")
        if error:
            print(f"   الخطأ: {error}")
        print()
    
    def phase1_setup_companies(self):
        """المرحلة 1: إعداد الشركات الأولية"""
        print("🏢 المرحلة 1: إعداد الشركات الأولية")
        print("=" * 50)
        
        try:
            # POST /api/setup-companies
            response = self.session.post(f"{BACKEND_URL}/setup-companies")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract company IDs - handle both new creation and existing companies
                if "master_seal_id" in data and "faster_seal_id" in data:
                    # New companies created
                    self.master_seal_id = data.get("master_seal_id")
                    self.faster_seal_id = data.get("faster_seal_id")
                else:
                    # Companies already exist, extract IDs from companies list
                    companies = data.get("companies", [])
                    master_seal = next((c for c in companies if c["name"] == "Master Seal"), None)
                    faster_seal = next((c for c in companies if c["name"] == "Faster Seal"), None)
                    
                    if master_seal:
                        self.master_seal_id = master_seal["id"]
                    if faster_seal:
                        self.faster_seal_id = faster_seal["id"]
                
                # Verify Master Seal colors
                companies = data.get("companies", [])
                master_seal = next((c for c in companies if c["name"] == "Master Seal"), None)
                faster_seal = next((c for c in companies if c["name"] == "Faster Seal"), None)
                
                if master_seal:
                    master_colors_correct = (
                        master_seal["primary_color"] == "#3B82F6" and 
                        master_seal["secondary_color"] == "#10B981"
                    )
                    self.log_test(
                        "إعداد Master Seal مع الألوان الصحيحة",
                        master_colors_correct,
                        f"الألوان: {master_seal['primary_color']} (أزرق), {master_seal['secondary_color']} (أخضر)"
                    )
                
                if faster_seal:
                    faster_colors_correct = (
                        faster_seal["primary_color"] == "#EF4444" and 
                        faster_seal["secondary_color"] == "#F97316"
                    )
                    self.log_test(
                        "إعداد Faster Seal مع الألوان الصحيحة",
                        faster_colors_correct,
                        f"الألوان: {faster_seal['primary_color']} (أحمر), {faster_seal['secondary_color']} (برتقالي)"
                    )
                
                self.log_test(
                    "إنشاء الشركات الأولية",
                    True,
                    f"تم إنشاء شركتين: Master Seal ID: {self.master_seal_id}, Faster Seal ID: {self.faster_seal_id}"
                )
                
            else:
                self.log_test(
                    "إنشاء الشركات الأولية",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("إنشاء الشركات الأولية", False, error=str(e))
    
    def phase2_migrate_data(self):
        """المرحلة 2: ترحيل البيانات الحالية"""
        print("📦 المرحلة 2: ترحيل البيانات الحالية")
        print("=" * 50)
        
        if not self.master_seal_id:
            self.log_test("ترحيل البيانات", False, error="معرف Master Seal غير متوفر")
            return
        
        try:
            # POST /api/migrate-data-to-company
            response = self.session.post(
                f"{BACKEND_URL}/migrate-data-to-company",
                params={"company_id": self.master_seal_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                migration_results = data.get("migration_results", {})
                total_migrated = data.get("total_migrated", 0)
                
                details = []
                for data_type, count in migration_results.items():
                    if count > 0:
                        details.append(f"{data_type}: {count}")
                
                self.log_test(
                    "ترحيل البيانات إلى Master Seal",
                    True,
                    f"إجمالي العناصر المرحلة: {total_migrated} - {', '.join(details)}"
                )
                
            else:
                self.log_test(
                    "ترحيل البيانات إلى Master Seal",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("ترحيل البيانات إلى Master Seal", False, error=str(e))
    
    def phase3_test_data_filtering(self):
        """المرحلة 3: اختبار فلترة البيانات بالشركات"""
        print("🔍 المرحلة 3: اختبار فلترة البيانات بالشركات")
        print("=" * 50)
        
        if not self.master_seal_id or not self.faster_seal_id:
            self.log_test("فلترة البيانات", False, error="معرفات الشركات غير متوفرة")
            return
        
        # Test raw materials filtering
        self._test_data_filtering("raw-materials", "المواد الخام")
        
        # Test invoices filtering
        self._test_data_filtering("invoices", "الفواتير")
        
        # Test customers filtering
        self._test_data_filtering("customers", "العملاء")
    
    def _test_data_filtering(self, endpoint, data_type_ar):
        """Helper function to test data filtering for specific endpoint"""
        try:
            # Test Master Seal data (should have migrated data)
            master_response = self.session.get(
                f"{BACKEND_URL}/{endpoint}",
                params={"company_id": self.master_seal_id}
            )
            
            if master_response.status_code == 200:
                master_data = master_response.json()
                master_count = len(master_data) if isinstance(master_data, list) else 0
                
                self.log_test(
                    f"استرجاع {data_type_ar} من Master Seal",
                    True,
                    f"تم العثور على {master_count} عنصر"
                )
            else:
                self.log_test(
                    f"استرجاع {data_type_ar} من Master Seal",
                    False,
                    error=f"HTTP {master_response.status_code}: {master_response.text}"
                )
            
            # Test Faster Seal data (should be empty)
            faster_response = self.session.get(
                f"{BACKEND_URL}/{endpoint}",
                params={"company_id": self.faster_seal_id}
            )
            
            if faster_response.status_code == 200:
                faster_data = faster_response.json()
                faster_count = len(faster_data) if isinstance(faster_data, list) else 0
                
                self.log_test(
                    f"استرجاع {data_type_ar} من Faster Seal (يجب أن يكون فارغ)",
                    faster_count == 0,
                    f"عدد العناصر: {faster_count} (المتوقع: 0)"
                )
            else:
                self.log_test(
                    f"استرجاع {data_type_ar} من Faster Seal",
                    False,
                    error=f"HTTP {faster_response.status_code}: {faster_response.text}"
                )
                
        except Exception as e:
            self.log_test(f"فلترة {data_type_ar}", False, error=str(e))
    
    def phase4_test_new_data_creation(self):
        """المرحلة 4: اختبار إنشاء بيانات جديدة"""
        print("🆕 المرحلة 4: اختبار إنشاء بيانات جديدة")
        print("=" * 50)
        
        if not self.faster_seal_id:
            self.log_test("إنشاء بيانات جديدة", False, error="معرف Faster Seal غير متوفر")
            return
        
        try:
            # Create new raw material in Faster Seal
            new_material = {
                "material_type": "NBR",
                "inner_diameter": 25.0,
                "outer_diameter": 35.0,
                "height": 8.0,
                "pieces_count": 10,
                "cost_per_mm": 2.5
            }
            
            # First, create inventory item to support raw material creation
            inventory_item = {
                "material_type": "NBR",
                "inner_diameter": 25.0,
                "outer_diameter": 35.0,
                "available_pieces": 50,
                "min_stock_level": 5,
                "notes": "مخزون اختبار لـ Faster Seal"
            }
            
            inventory_response = self.session.post(
                f"{BACKEND_URL}/inventory",
                json=inventory_item
            )
            
            if inventory_response.status_code == 200:
                self.log_test(
                    "إنشاء عنصر مخزون لدعم المادة الخام",
                    True,
                    "تم إنشاء عنصر المخزون بنجاح"
                )
            
            # Now create raw material
            material_response = self.session.post(
                f"{BACKEND_URL}/raw-materials",
                json=new_material,
                params={"company_id": self.faster_seal_id}
            )
            
            if material_response.status_code == 200:
                created_material = material_response.json()
                material_id = created_material.get("id")
                
                self.log_test(
                    "إنشاء مادة خام جديدة في Faster Seal",
                    True,
                    f"تم إنشاء المادة بمعرف: {material_id}"
                )
                
                # Verify it appears in Faster Seal
                faster_materials = self.session.get(
                    f"{BACKEND_URL}/raw-materials",
                    params={"company_id": self.faster_seal_id}
                ).json()
                
                faster_has_material = any(m.get("id") == material_id for m in faster_materials)
                
                self.log_test(
                    "المادة الجديدة تظهر في Faster Seal",
                    faster_has_material,
                    f"عدد المواد في Faster Seal: {len(faster_materials)}"
                )
                
                # Verify it doesn't appear in Master Seal
                master_materials = self.session.get(
                    f"{BACKEND_URL}/raw-materials",
                    params={"company_id": self.master_seal_id}
                ).json()
                
                master_has_material = any(m.get("id") == material_id for m in master_materials)
                
                self.log_test(
                    "المادة الجديدة لا تظهر في Master Seal",
                    not master_has_material,
                    f"عدد المواد في Master Seal: {len(master_materials)}"
                )
                
            else:
                self.log_test(
                    "إنشاء مادة خام جديدة في Faster Seal",
                    False,
                    error=f"HTTP {material_response.status_code}: {material_response.text}"
                )
                
        except Exception as e:
            self.log_test("إنشاء بيانات جديدة", False, error=str(e))
    
    def phase5_test_user_permissions(self):
        """المرحلة 5: اختبار صلاحيات المستخدمين"""
        print("👤 المرحلة 5: اختبار صلاحيات المستخدمين")
        print("=" * 50)
        
        try:
            # GET /api/user-companies/Elsawy
            response = self.session.get(f"{BACKEND_URL}/user-companies/Elsawy")
            
            if response.status_code == 200:
                user_companies = response.json()
                
                # Check if Elsawy has access to both companies
                company_ids = [comp.get("id") for comp in user_companies]
                has_master_access = self.master_seal_id in company_ids
                has_faster_access = self.faster_seal_id in company_ids
                
                # Check admin privileges
                master_access = next((c for c in user_companies if c.get("id") == self.master_seal_id), None)
                faster_access = next((c for c in user_companies if c.get("id") == self.faster_seal_id), None)
                
                master_admin = master_access and master_access.get("access_level") == "admin" if master_access else False
                faster_admin = faster_access and faster_access.get("access_level") == "admin" if faster_access else False
                
                self.log_test(
                    "Elsawy لديه وصول لـ Master Seal",
                    has_master_access,
                    f"صلاحية admin: {master_admin}"
                )
                
                self.log_test(
                    "Elsawy لديه وصول لـ Faster Seal",
                    has_faster_access,
                    f"صلاحية admin: {faster_admin}"
                )
                
                self.log_test(
                    "Elsawy لديه صلاحية admin للشركتين",
                    master_admin and faster_admin,
                    f"إجمالي الشركات المتاحة: {len(user_companies)}"
                )
                
            else:
                self.log_test(
                    "استرجاع صلاحيات Elsawy",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("اختبار صلاحيات المستخدمين", False, error=str(e))
    
    def phase6_test_company_management_apis(self):
        """المرحلة 6: اختبار APIs إدارة الشركات"""
        print("🏗️ المرحلة 6: اختبار APIs إدارة الشركات")
        print("=" * 50)
        
        try:
            # GET /api/companies - list all companies
            companies_response = self.session.get(f"{BACKEND_URL}/companies")
            
            if companies_response.status_code == 200:
                companies = companies_response.json()
                company_names = [comp.get("name") for comp in companies]
                
                has_master = "Master Seal" in company_names
                has_faster = "Faster Seal" in company_names
                
                self.log_test(
                    "استرجاع قائمة جميع الشركات",
                    len(companies) >= 2,
                    f"عدد الشركات: {len(companies)} - الأسماء: {', '.join(company_names)}"
                )
                
                self.log_test(
                    "Master Seal موجودة في القائمة",
                    has_master,
                    "تم العثور على Master Seal"
                )
                
                self.log_test(
                    "Faster Seal موجودة في القائمة",
                    has_faster,
                    "تم العثور على Faster Seal"
                )
                
            else:
                self.log_test(
                    "استرجاع قائمة الشركات",
                    False,
                    error=f"HTTP {companies_response.status_code}: {companies_response.text}"
                )
            
            # Test specific company details
            if self.master_seal_id:
                master_response = self.session.get(f"{BACKEND_URL}/companies/{self.master_seal_id}")
                
                if master_response.status_code == 200:
                    master_details = master_response.json()
                    
                    self.log_test(
                        "استرجاع تفاصيل Master Seal",
                        True,
                        f"الاسم: {master_details.get('name')}, الألوان: {master_details.get('primary_color')}/{master_details.get('secondary_color')}"
                    )
                else:
                    self.log_test(
                        "استرجاع تفاصيل Master Seal",
                        False,
                        error=f"HTTP {master_response.status_code}: {master_response.text}"
                    )
            
            if self.faster_seal_id:
                faster_response = self.session.get(f"{BACKEND_URL}/companies/{self.faster_seal_id}")
                
                if faster_response.status_code == 200:
                    faster_details = faster_response.json()
                    
                    self.log_test(
                        "استرجاع تفاصيل Faster Seal",
                        True,
                        f"الاسم: {faster_details.get('name')}, الألوان: {faster_details.get('primary_color')}/{faster_details.get('secondary_color')}"
                    )
                else:
                    self.log_test(
                        "استرجاع تفاصيل Faster Seal",
                        False,
                        error=f"HTTP {faster_response.status_code}: {faster_response.text}"
                    )
                
        except Exception as e:
            self.log_test("اختبار APIs إدارة الشركات", False, error=str(e))
    
    def run_comprehensive_test(self):
        """تشغيل الاختبار الشامل لنظام Multi-Company"""
        print("🚀 بدء الاختبار الشامل لنظام Multi-Company")
        print("=" * 60)
        print()
        
        # Run all phases
        self.phase1_setup_companies()
        self.phase2_migrate_data()
        self.phase3_test_data_filtering()
        self.phase4_test_new_data_creation()
        self.phase5_test_user_permissions()
        self.phase6_test_company_management_apis()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("📊 ملخص نتائج الاختبار")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"إجمالي الاختبارات: {total_tests}")
        print(f"الاختبارات الناجحة: {passed_tests} ✅")
        print(f"الاختبارات الفاشلة: {failed_tests} ❌")
        print(f"نسبة النجاح: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("الاختبارات الفاشلة:")
            print("-" * 30)
            for test in self.test_results:
                if not test["success"]:
                    print(f"❌ {test['test']}")
                    if test["error"]:
                        print(f"   الخطأ: {test['error']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 تقييم عام: ممتاز - نظام Multi-Company يعمل بشكل مثالي!")
        elif success_rate >= 75:
            print("✅ تقييم عام: جيد - نظام Multi-Company يعمل مع بعض المشاكل البسيطة")
        elif success_rate >= 50:
            print("⚠️ تقييم عام: متوسط - نظام Multi-Company يحتاج إصلاحات")
        else:
            print("🚨 تقييم عام: ضعيف - نظام Multi-Company يحتاج إعادة تطوير")
        
        print()
        print("تم الانتهاء من اختبار نظام Multi-Company!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "overall_status": "excellent" if success_rate >= 90 else "good" if success_rate >= 75 else "average" if success_rate >= 50 else "poor"
        }

def main():
    """Main function to run the multi-company system test"""
    tester = MultiCompanyTester()
    
    try:
        summary = tester.run_comprehensive_test()
        
        # Exit with appropriate code
        if summary["success_rate"] >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار بواسطة المستخدم")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 خطأ غير متوقع: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main()