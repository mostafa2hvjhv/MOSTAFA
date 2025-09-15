#!/usr/bin/env python3
"""
اختبار إصلاح مشكلة تحويل طريقة الدفع مع "الآجل"
Testing Payment Method Conversion Bug Fix with Deferred Payment

This test file specifically tests the payment method conversion functionality
as requested by the user to verify the bug fix.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

class PaymentMethodConversionTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.created_invoices = []
        self.created_customers = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to backend API"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    return await response.json(), response.status
        except Exception as e:
            return {"error": str(e)}, 500
            
    def log_test_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ نجح" if success else "❌ فشل"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}")
        if details:
            print(f"   التفاصيل: {details}")
        if error:
            print(f"   الخطأ: {error}")
        print()
        
    async def create_test_customer(self, name):
        """Create a test customer"""
        customer_data = {
            "name": name,
            "phone": "01234567890",
            "address": "عنوان اختبار"
        }
        
        response, status = await self.make_request("POST", "/customers", customer_data)
        if status == 200:
            self.created_customers.append(response["id"])
            return response
        return None
        
    async def create_test_invoice(self, customer_name, payment_method, amount=500.0):
        """Create a test invoice with specified payment method"""
        invoice_data = {
            "customer_name": customer_name,
            "invoice_title": f"فاتورة اختبار تحويل طريقة الدفع - {payment_method}",
            "supervisor_name": "مشرف الاختبار",
            "items": [
                {
                    "product_type": "local",
                    "product_name": "منتج اختبار",
                    "quantity": 1,
                    "unit_price": amount,
                    "total_price": amount,
                    "local_product_details": {
                        "name": "منتج اختبار",
                        "supplier": "مورد اختبار",
                        "purchase_price": amount * 0.7,
                        "selling_price": amount,
                        "product_size": "حجم اختبار",
                        "product_type": "نوع اختبار"
                    }
                }
            ],
            "payment_method": payment_method,
            "discount_type": "amount",
            "discount_value": 0.0,
            "notes": "فاتورة اختبار لتحويل طريقة الدفع"
        }
        
        response, status = await self.make_request("POST", "/invoices", invoice_data)
        if status == 200:
            self.created_invoices.append(response["id"])
            return response
        return None
        
    async def get_invoice(self, invoice_id):
        """Get invoice details"""
        response, status = await self.make_request("GET", f"/invoices/{invoice_id}")
        if status == 200:
            return response
        return None
        
    async def get_treasury_transactions(self):
        """Get all treasury transactions"""
        response, status = await self.make_request("GET", "/treasury/transactions")
        if status == 200:
            return response
        return []
        
    async def change_payment_method(self, invoice_id, new_payment_method):
        """Change invoice payment method"""
        params = {
            "new_payment_method": new_payment_method,
            "username": "Elsawy"
        }
        response, status = await self.make_request("PUT", f"/invoices/{invoice_id}/change-payment-method", params=params)
        return response, status
        
    async def test_cash_to_deferred_conversion(self):
        """Test 1: تحويل من النقدي إلى الآجل"""
        test_name = "تحويل من النقدي إلى الآجل"
        
        try:
            # Create customer
            customer = await self.create_test_customer("عميل اختبار النقدي إلى الآجل")
            if not customer:
                self.log_test_result(test_name, False, error="فشل في إنشاء العميل")
                return
                
            # Create cash invoice
            invoice = await self.create_test_invoice(customer["name"], "نقدي", 500.0)
            if not invoice:
                self.log_test_result(test_name, False, error="فشل في إنشاء الفاتورة النقدية")
                return
                
            # Verify initial state
            if invoice["payment_method"] != "نقدي" or invoice["remaining_amount"] != 0:
                self.log_test_result(test_name, False, error=f"الحالة الأولية خاطئة - طريقة الدفع: {invoice['payment_method']}, المبلغ المتبقي: {invoice['remaining_amount']}")
                return
                
            # Get treasury transactions before conversion
            treasury_before = await self.get_treasury_transactions()
            cash_transactions_before = [t for t in treasury_before if t.get("account_id") == "cash"]
            
            # Convert to deferred
            conversion_response, status = await self.change_payment_method(invoice["id"], "آجل")
            if status != 200:
                self.log_test_result(test_name, False, error=f"فشل في تحويل طريقة الدفع - كود الخطأ: {status}, الاستجابة: {conversion_response}")
                return
                
            # Verify conversion response
            if "طريقة الدفع غير مدعومة" in str(conversion_response):
                self.log_test_result(test_name, False, error="ظهرت رسالة 'طريقة الدفع غير مدعومة'")
                return
                
            # Get updated invoice
            updated_invoice = await self.get_invoice(invoice["id"])
            if not updated_invoice:
                self.log_test_result(test_name, False, error="فشل في استرجاع الفاتورة المحدثة")
                return
                
            # Verify invoice updates
            success = True
            details = []
            
            if updated_invoice["payment_method"] != "آجل":
                success = False
                details.append(f"طريقة الدفع لم تتحدث - متوقع: آجل, فعلي: {updated_invoice['payment_method']}")
                
            if updated_invoice["remaining_amount"] != updated_invoice["total_amount"]:
                success = False
                details.append(f"المبلغ المتبقي خاطئ - متوقع: {updated_invoice['total_amount']}, فعلي: {updated_invoice['remaining_amount']}")
                
            # Get treasury transactions after conversion
            treasury_after = await self.get_treasury_transactions()
            cash_transactions_after = [t for t in treasury_after if t.get("account_id") == "cash"]
            
            # Check if expense transaction was created to remove from cash
            new_cash_transactions = [t for t in cash_transactions_after if t not in cash_transactions_before]
            expense_transactions = [t for t in new_cash_transactions if t.get("transaction_type") == "expense"]
            
            if not expense_transactions:
                success = False
                details.append("لم يتم إنشاء معاملة خزينة expense لإزالة المبلغ من النقدي")
            else:
                expense_transaction = expense_transactions[0]
                if expense_transaction["amount"] != invoice["total_amount"]:
                    success = False
                    details.append(f"مبلغ معاملة الخزينة خاطئ - متوقع: {invoice['total_amount']}, فعلي: {expense_transaction['amount']}")
                    
            if success:
                details.append(f"تم التحويل بنجاح من النقدي إلى الآجل")
                details.append(f"المبلغ المتبقي: {updated_invoice['remaining_amount']} ج.م")
                details.append(f"تم إنشاء معاملة خزينة expense بقيمة {expense_transactions[0]['amount']} ج.م")
                
            self.log_test_result(test_name, success, "; ".join(details))
            
        except Exception as e:
            self.log_test_result(test_name, False, error=str(e))
            
    async def test_deferred_to_cash_conversion(self):
        """Test 2: تحويل من الآجل إلى النقدي"""
        test_name = "تحويل من الآجل إلى النقدي"
        
        try:
            # Create customer
            customer = await self.create_test_customer("عميل اختبار الآجل إلى النقدي")
            if not customer:
                self.log_test_result(test_name, False, error="فشل في إنشاء العميل")
                return
                
            # Create deferred invoice
            invoice = await self.create_test_invoice(customer["name"], "آجل", 600.0)
            if not invoice:
                self.log_test_result(test_name, False, error="فشل في إنشاء الفاتورة الآجلة")
                return
                
            # Verify initial state
            if invoice["payment_method"] != "آجل" or invoice["remaining_amount"] != invoice["total_amount"]:
                self.log_test_result(test_name, False, error=f"الحالة الأولية خاطئة - طريقة الدفع: {invoice['payment_method']}, المبلغ المتبقي: {invoice['remaining_amount']}")
                return
                
            # Get treasury transactions before conversion
            treasury_before = await self.get_treasury_transactions()
            cash_transactions_before = [t for t in treasury_before if t.get("account_id") == "cash"]
            
            # Convert to cash
            conversion_response, status = await self.change_payment_method(invoice["id"], "نقدي")
            if status != 200:
                self.log_test_result(test_name, False, error=f"فشل في تحويل طريقة الدفع - كود الخطأ: {status}, الاستجابة: {conversion_response}")
                return
                
            # Verify conversion response
            if "طريقة الدفع غير مدعومة" in str(conversion_response):
                self.log_test_result(test_name, False, error="ظهرت رسالة 'طريقة الدفع غير مدعومة'")
                return
                
            # Get updated invoice
            updated_invoice = await self.get_invoice(invoice["id"])
            if not updated_invoice:
                self.log_test_result(test_name, False, error="فشل في استرجاع الفاتورة المحدثة")
                return
                
            # Verify invoice updates
            success = True
            details = []
            
            if updated_invoice["payment_method"] != "نقدي":
                success = False
                details.append(f"طريقة الدفع لم تتحدث - متوقع: نقدي, فعلي: {updated_invoice['payment_method']}")
                
            if updated_invoice["remaining_amount"] != 0:
                success = False
                details.append(f"المبلغ المتبقي خاطئ - متوقع: 0, فعلي: {updated_invoice['remaining_amount']}")
                
            # Get treasury transactions after conversion
            treasury_after = await self.get_treasury_transactions()
            cash_transactions_after = [t for t in treasury_after if t.get("account_id") == "cash"]
            
            # Check if income transaction was created to add to cash
            new_cash_transactions = [t for t in cash_transactions_after if t not in cash_transactions_before]
            income_transactions = [t for t in new_cash_transactions if t.get("transaction_type") == "income"]
            
            if not income_transactions:
                success = False
                details.append("لم يتم إنشاء معاملة خزينة income لإضافة المبلغ للنقدي")
            else:
                income_transaction = income_transactions[0]
                if income_transaction["amount"] != invoice["total_amount"]:
                    success = False
                    details.append(f"مبلغ معاملة الخزينة خاطئ - متوقع: {invoice['total_amount']}, فعلي: {income_transaction['amount']}")
                    
            if success:
                details.append(f"تم التحويل بنجاح من الآجل إلى النقدي")
                details.append(f"المبلغ المتبقي: {updated_invoice['remaining_amount']} ج.م")
                details.append(f"تم إنشاء معاملة خزينة income بقيمة {income_transactions[0]['amount']} ج.م")
                
            self.log_test_result(test_name, success, "; ".join(details))
            
        except Exception as e:
            self.log_test_result(test_name, False, error=str(e))
            
    async def test_deferred_to_vodafone_conversion(self):
        """Test 3: تحويل من الآجل إلى فودافون كاش"""
        test_name = "تحويل من الآجل إلى فودافون كاش محمد الصاوي"
        
        try:
            # Create customer
            customer = await self.create_test_customer("عميل اختبار الآجل إلى فودافون")
            if not customer:
                self.log_test_result(test_name, False, error="فشل في إنشاء العميل")
                return
                
            # Create deferred invoice
            invoice = await self.create_test_invoice(customer["name"], "آجل", 400.0)
            if not invoice:
                self.log_test_result(test_name, False, error="فشل في إنشاء الفاتورة الآجلة")
                return
                
            # Get treasury transactions before conversion
            treasury_before = await self.get_treasury_transactions()
            vodafone_transactions_before = [t for t in treasury_before if t.get("account_id") == "vodafone_elsawy"]
            
            # Convert to Vodafone Cash
            conversion_response, status = await self.change_payment_method(invoice["id"], "فودافون كاش محمد الصاوي")
            if status != 200:
                self.log_test_result(test_name, False, error=f"فشل في تحويل طريقة الدفع - كود الخطأ: {status}, الاستجابة: {conversion_response}")
                return
                
            # Verify conversion response
            if "طريقة الدفع غير مدعومة" in str(conversion_response):
                self.log_test_result(test_name, False, error="ظهرت رسالة 'طريقة الدفع غير مدعومة'")
                return
                
            # Get updated invoice
            updated_invoice = await self.get_invoice(invoice["id"])
            if not updated_invoice:
                self.log_test_result(test_name, False, error="فشل في استرجاع الفاتورة المحدثة")
                return
                
            # Verify invoice updates
            success = True
            details = []
            
            if updated_invoice["payment_method"] != "فودافون كاش محمد الصاوي":
                success = False
                details.append(f"طريقة الدفع لم تتحدث - متوقع: فودافون كاش محمد الصاوي, فعلي: {updated_invoice['payment_method']}")
                
            if updated_invoice["remaining_amount"] != 0:
                success = False
                details.append(f"المبلغ المتبقي خاطئ - متوقع: 0, فعلي: {updated_invoice['remaining_amount']}")
                
            # Get treasury transactions after conversion
            treasury_after = await self.get_treasury_transactions()
            vodafone_transactions_after = [t for t in treasury_after if t.get("account_id") == "vodafone_elsawy"]
            
            # Check if income transaction was created for Vodafone
            new_vodafone_transactions = [t for t in vodafone_transactions_after if t not in vodafone_transactions_before]
            income_transactions = [t for t in new_vodafone_transactions if t.get("transaction_type") == "income"]
            
            if not income_transactions:
                success = False
                details.append("لم يتم إنشاء معاملة خزينة income لفودافون كاش")
            else:
                income_transaction = income_transactions[0]
                if income_transaction["amount"] != invoice["total_amount"]:
                    success = False
                    details.append(f"مبلغ معاملة الخزينة خاطئ - متوقع: {invoice['total_amount']}, فعلي: {income_transaction['amount']}")
                    
            if success:
                details.append(f"تم التحويل بنجاح من الآجل إلى فودافون كاش")
                details.append(f"المبلغ المتبقي: {updated_invoice['remaining_amount']} ج.م")
                details.append(f"تم إنشاء معاملة خزينة income بقيمة {income_transactions[0]['amount']} ج.م")
                
            self.log_test_result(test_name, success, "; ".join(details))
            
        except Exception as e:
            self.log_test_result(test_name, False, error=str(e))
            
    async def test_vodafone_to_deferred_conversion(self):
        """Test 4: تحويل من فودافون كاش إلى الآجل"""
        test_name = "تحويل من فودافون كاش محمد الصاوي إلى الآجل"
        
        try:
            # Create customer
            customer = await self.create_test_customer("عميل اختبار فودافون إلى الآجل")
            if not customer:
                self.log_test_result(test_name, False, error="فشل في إنشاء العميل")
                return
                
            # Create Vodafone invoice
            invoice = await self.create_test_invoice(customer["name"], "فودافون كاش محمد الصاوي", 350.0)
            if not invoice:
                self.log_test_result(test_name, False, error="فشل في إنشاء فاتورة فودافون كاش")
                return
                
            # Get treasury transactions before conversion
            treasury_before = await self.get_treasury_transactions()
            vodafone_transactions_before = [t for t in treasury_before if t.get("account_id") == "vodafone_elsawy"]
            
            # Convert to deferred
            conversion_response, status = await self.change_payment_method(invoice["id"], "آجل")
            if status != 200:
                self.log_test_result(test_name, False, error=f"فشل في تحويل طريقة الدفع - كود الخطأ: {status}, الاستجابة: {conversion_response}")
                return
                
            # Verify conversion response
            if "طريقة الدفع غير مدعومة" in str(conversion_response):
                self.log_test_result(test_name, False, error="ظهرت رسالة 'طريقة الدفع غير مدعومة'")
                return
                
            # Get updated invoice
            updated_invoice = await self.get_invoice(invoice["id"])
            if not updated_invoice:
                self.log_test_result(test_name, False, error="فشل في استرجاع الفاتورة المحدثة")
                return
                
            # Verify invoice updates
            success = True
            details = []
            
            if updated_invoice["payment_method"] != "آجل":
                success = False
                details.append(f"طريقة الدفع لم تتحدث - متوقع: آجل, فعلي: {updated_invoice['payment_method']}")
                
            if updated_invoice["remaining_amount"] != updated_invoice["total_amount"]:
                success = False
                details.append(f"المبلغ المتبقي خاطئ - متوقع: {updated_invoice['total_amount']}, فعلي: {updated_invoice['remaining_amount']}")
                
            # Get treasury transactions after conversion
            treasury_after = await self.get_treasury_transactions()
            vodafone_transactions_after = [t for t in treasury_after if t.get("account_id") == "vodafone_elsawy"]
            
            # Check if expense transaction was created to remove from Vodafone
            new_vodafone_transactions = [t for t in vodafone_transactions_after if t not in vodafone_transactions_before]
            expense_transactions = [t for t in new_vodafone_transactions if t.get("transaction_type") == "expense"]
            
            if not expense_transactions:
                success = False
                details.append("لم يتم إنشاء معاملة خزينة expense لإزالة المبلغ من فودافون كاش")
            else:
                expense_transaction = expense_transactions[0]
                if expense_transaction["amount"] != invoice["total_amount"]:
                    success = False
                    details.append(f"مبلغ معاملة الخزينة خاطئ - متوقع: {invoice['total_amount']}, فعلي: {expense_transaction['amount']}")
                    
            if success:
                details.append(f"تم التحويل بنجاح من فودافون كاش إلى الآجل")
                details.append(f"المبلغ المتبقي: {updated_invoice['remaining_amount']} ج.م")
                details.append(f"تم إنشاء معاملة خزينة expense بقيمة {expense_transactions[0]['amount']} ج.م")
                
            self.log_test_result(test_name, success, "; ".join(details))
            
        except Exception as e:
            self.log_test_result(test_name, False, error=str(e))
            
    async def test_unsupported_payment_method_error(self):
        """Test 5: اختبار رسالة خطأ طريقة الدفع غير المدعومة"""
        test_name = "اختبار رسالة خطأ طريقة الدفع غير المدعومة"
        
        try:
            # Create customer
            customer = await self.create_test_customer("عميل اختبار طريقة دفع غير مدعومة")
            if not customer:
                self.log_test_result(test_name, False, error="فشل في إنشاء العميل")
                return
                
            # Create cash invoice
            invoice = await self.create_test_invoice(customer["name"], "نقدي", 100.0)
            if not invoice:
                self.log_test_result(test_name, False, error="فشل في إنشاء الفاتورة")
                return
                
            # Try to convert to unsupported payment method
            conversion_response, status = await self.change_payment_method(invoice["id"], "طريقة دفع غير موجودة")
            
            success = False
            details = []
            
            if status == 400 and "طريقة الدفع غير مدعومة" in str(conversion_response):
                success = True
                details.append("تم إرجاع رسالة الخطأ الصحيحة للطريقة غير المدعومة")
            else:
                details.append(f"لم يتم إرجاع رسالة الخطأ المتوقعة - كود الاستجابة: {status}, الرسالة: {conversion_response}")
                
            self.log_test_result(test_name, success, "; ".join(details))
            
        except Exception as e:
            self.log_test_result(test_name, False, error=str(e))
            
    async def cleanup_test_data(self):
        """Clean up test data"""
        print("🧹 تنظيف بيانات الاختبار...")
        
        # Delete created invoices
        for invoice_id in self.created_invoices:
            try:
                await self.make_request("DELETE", f"/invoices/{invoice_id}")
            except:
                pass
                
        # Delete created customers
        for customer_id in self.created_customers:
            try:
                await self.make_request("DELETE", f"/customers/{customer_id}")
            except:
                pass
                
        print(f"تم حذف {len(self.created_invoices)} فاتورة و {len(self.created_customers)} عميل")
        
    async def run_all_tests(self):
        """Run all payment method conversion tests"""
        print("🚀 بدء اختبار إصلاح مشكلة تحويل طريقة الدفع مع الآجل")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Run all tests
            await self.test_cash_to_deferred_conversion()
            await self.test_deferred_to_cash_conversion()
            await self.test_deferred_to_vodafone_conversion()
            await self.test_vodafone_to_deferred_conversion()
            await self.test_unsupported_payment_method_error()
            
        finally:
            await self.cleanup_test_data()
            await self.cleanup_session()
            
        # Print summary
        print("=" * 60)
        print("📊 ملخص نتائج الاختبار:")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"إجمالي الاختبارات: {total_tests}")
        print(f"الاختبارات الناجحة: {passed_tests} ✅")
        print(f"الاختبارات الفاشلة: {failed_tests} ❌")
        print(f"نسبة النجاح: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("🚨 الاختبارات الفاشلة:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}")
                    if result["error"]:
                        print(f"   الخطأ: {result['error']}")
        else:
            print("🎉 جميع الاختبارات نجحت! إصلاح مشكلة تحويل طريقة الدفع يعمل بشكل مثالي.")
            
        return success_rate >= 80  # Consider 80%+ as overall success

async def main():
    """Main test function"""
    tester = PaymentMethodConversionTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ اختبار إصلاح مشكلة تحويل طريقة الدفع مع الآجل مكتمل بنجاح!")
        sys.exit(0)
    else:
        print("\n❌ فشل في اختبار إصلاح مشكلة تحويل طريقة الدفع مع الآجل!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())