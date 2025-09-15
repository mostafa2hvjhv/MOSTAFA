#!/usr/bin/env python3
"""
Quick test for the fixed APIs
"""

import requests
import json
import uuid
from datetime import datetime

BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

def test_export_api():
    """Test the fixed export API"""
    print("Testing GET /api/data-management/export-all...")
    
    response = requests.get(f"{BACKEND_URL}/data-management/export-all")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Export API works! Contains: {list(data.get('data', {}).keys())}")
        return True
    else:
        print(f"❌ Export API failed: HTTP {response.status_code}")
        return False

def test_raw_materials_bulk_import():
    """Test the fixed raw materials bulk import"""
    print("Testing POST /api/raw-materials/bulk-import...")
    
    test_data = {
        "data": [
            {
                "material_type": "NBR",
                "inner_diameter": 15.0,
                "outer_diameter": 25.0,
                "height": 100.0,
                "pieces_count": 10,
                "unit_code": f"QUICK-TEST-{datetime.now().strftime('%H%M%S')}",
                "cost_per_mm": 0.5
            }
        ]
    }
    
    response = requests.post(f"{BACKEND_URL}/raw-materials/bulk-import", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Raw materials bulk import works! Imported: {result.get('imported', 0)}")
        return True
    else:
        print(f"❌ Raw materials bulk import failed: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    print("🔧 Quick Fix Test")
    print("=" * 30)
    
    export_ok = test_export_api()
    import_ok = test_raw_materials_bulk_import()
    
    if export_ok and import_ok:
        print("\n✅ All fixes working!")
    else:
        print("\n❌ Some fixes still need work")