#!/usr/bin/env python3
"""
Simple Multi-Company System Test - اختبار مبسط لنظام الشركات المتعددة
"""

import requests
import json

BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

def test_companies_setup():
    """Test companies setup and basic functionality"""
    print("🏢 اختبار إعداد الشركات")
    print("=" * 40)
    
    # Test 1: Get companies list
    try:
        response = requests.get(f"{BACKEND_URL}/companies")
        if response.status_code == 200:
            companies = response.json()
            print(f"✅ تم العثور على {len(companies)} شركة")
            
            master_seal = None
            faster_seal = None
            
            for company in companies:
                print(f"   - {company['name']} (ID: {company['id']})")
                if company['name'] == 'Master Seal':
                    master_seal = company
                elif company['name'] == 'Faster Seal':
                    faster_seal = company
            
            # Test colors
            if master_seal:
                colors_ok = (master_seal['primary_color'] == '#3B82F6' and 
                           master_seal['secondary_color'] == '#10B981')
                print(f"✅ Master Seal colors: {colors_ok}")
                
            if faster_seal:
                colors_ok = (faster_seal['primary_color'] == '#EF4444' and 
                           faster_seal['secondary_color'] == '#F97316')
                print(f"✅ Faster Seal colors: {colors_ok}")
                
            return master_seal, faster_seal
            
        else:
            print(f"❌ خطأ في استرجاع الشركات: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return None, None

def test_data_filtering(master_seal, faster_seal):
    """Test data filtering by company"""
    print("\n🔍 اختبار فلترة البيانات")
    print("=" * 40)
    
    if not master_seal or not faster_seal:
        print("❌ معرفات الشركات غير متوفرة")
        return
    
    master_id = master_seal['id']
    faster_id = faster_seal['id']
    
    # Test raw materials filtering
    endpoints = [
        ('raw-materials', 'المواد الخام'),
        ('invoices', 'الفواتير'),
        ('customers', 'العملاء')
    ]
    
    for endpoint, name_ar in endpoints:
        try:
            # Test Master Seal
            master_response = requests.get(f"{BACKEND_URL}/{endpoint}", 
                                         params={"company_id": master_id})
            
            if master_response.status_code == 200:
                master_data = master_response.json()
                master_count = len(master_data) if isinstance(master_data, list) else 0
                print(f"✅ Master Seal {name_ar}: {master_count} عنصر")
            else:
                print(f"❌ Master Seal {name_ar}: خطأ {master_response.status_code}")
            
            # Test Faster Seal
            faster_response = requests.get(f"{BACKEND_URL}/{endpoint}", 
                                         params={"company_id": faster_id})
            
            if faster_response.status_code == 200:
                faster_data = faster_response.json()
                faster_count = len(faster_data) if isinstance(faster_data, list) else 0
                print(f"✅ Faster Seal {name_ar}: {faster_count} عنصر")
            else:
                print(f"❌ Faster Seal {name_ar}: خطأ {faster_response.status_code}")
                
        except Exception as e:
            print(f"❌ خطأ في اختبار {name_ar}: {str(e)}")

def test_data_migration(master_seal):
    """Test data migration"""
    print("\n📦 اختبار ترحيل البيانات")
    print("=" * 40)
    
    if not master_seal:
        print("❌ معرف Master Seal غير متوفر")
        return
    
    try:
        response = requests.post(f"{BACKEND_URL}/migrate-data-to-company",
                               params={"company_id": master_seal['id']})
        
        if response.status_code == 200:
            data = response.json()
            migration_results = data.get("migration_results", {})
            total_migrated = data.get("total_migrated", 0)
            
            print(f"✅ تم ترحيل {total_migrated} عنصر إجمالي")
            for data_type, count in migration_results.items():
                if count > 0:
                    print(f"   - {data_type}: {count}")
        else:
            print(f"❌ خطأ في الترحيل: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ خطأ في الترحيل: {str(e)}")

def main():
    """Main test function"""
    print("🚀 اختبار نظام Multi-Company المبسط")
    print("=" * 50)
    
    # Test 1: Setup and get companies
    master_seal, faster_seal = test_companies_setup()
    
    # Test 2: Data migration
    test_data_migration(master_seal)
    
    # Test 3: Data filtering
    test_data_filtering(master_seal, faster_seal)
    
    print("\n✅ انتهى الاختبار المبسط")

if __name__ == "__main__":
    main()