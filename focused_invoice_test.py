#!/usr/bin/env python3
"""
Focused Invoice Management API Testing using existing invoices
اختبار مركز لـ APIs إدارة الفواتير باستخدام الفواتير الموجودة
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://seal-inventory.preview.emergentagent.com/api"

class FocusedInvoiceTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
    
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
    
    def get_existing_invoices(self):
        """Get existing invoices for testing"""
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices")
            if response.status_code == 200:
                invoices = response.json()
                # Filter for recent invoices that are likely to have proper data
                recent_invoices = [inv for inv in invoices if inv.get('invoice_number', '').startswith('INV-0000')]
                return recent_invoices[:5]  # Take first 5 for testing
            return []
        except Exception as e:
            print(f"Error getting invoices: {e}")
            return []
    
    def test_payment_method_change_existing(self):
        """Test payment method change with existing invoices"""
        print("\n=== Testing Payment Method Change with Existing Invoices ===")
        
        invoices = self.get_existing_invoices()
        if not invoices:
            self.log_test("Get existing invoices", False, "No invoices found")
            return
        
        self.log_test("Get existing invoices", True, f"Found {len(invoices)} invoices")
        
        # Test 1: Change payment method of first invoice
        try:
            invoice = invoices[0]
            original_method = invoice.get('payment_method')
            invoice_id = invoice.get('id')
            invoice_number = invoice.get('invoice_number')
            amount = invoice.get('total_amount', 0)
            
            print(f"\nTesting with Invoice {invoice_number} (Amount: {amount}, Current method: {original_method})")
            
            # Get treasury balances before
            response = self.session.get(f"{BACKEND_URL}/treasury/balances")
            if response.status_code == 200:
                balances_before = response.json()
                
                # Change to a different payment method
                new_method = "فودافون كاش محمد الصاوي" if original_method != "فودافون كاش محمد الصاوي" else "انستاباي"
                
                response = self.session.put(
                    f"{BACKEND_URL}/invoices/{invoice_id}/change-payment-method",
                    params={"new_payment_method": new_method}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(f"Change payment method {invoice_number}", True, 
                                f"From {original_method} to {new_method}, Amount: {result.get('amount_transferred')}")
                    
                    # Verify treasury changes
                    response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                    if response.status_code == 200:
                        balances_after = response.json()
                        
                        # Map payment methods to account IDs
                        account_mapping = {
                            "نقدي": "cash",
                            "فودافون كاش محمد الصاوي": "vodafone_elsawy",
                            "فودافون كاش وائل محمد": "vodafone_wael",
                            "انستاباي": "instapay",
                            "يد الصاوي": "yad_elsawy"
                        }
                        
                        old_account = account_mapping.get(original_method)
                        new_account = account_mapping.get(new_method)
                        
                        if old_account and new_account:
                            old_balance_before = balances_before.get(old_account, 0)
                            old_balance_after = balances_after.get(old_account, 0)
                            new_balance_before = balances_before.get(new_account, 0)
                            new_balance_after = balances_after.get(new_account, 0)
                            
                            old_diff = old_balance_before - old_balance_after
                            new_diff = new_balance_after - new_balance_before
                            
                            if abs(old_diff - amount) < 0.01 and abs(new_diff - amount) < 0.01:
                                self.log_test("Treasury balance verification", True, 
                                            f"Old account reduced by {old_diff}, New account increased by {new_diff}")
                            else:
                                self.log_test("Treasury balance verification", False, 
                                            f"Expected {amount}, Old diff: {old_diff}, New diff: {new_diff}")
                    
                    # Verify invoice updated
                    response = self.session.get(f"{BACKEND_URL}/invoices/{invoice_id}")
                    if response.status_code == 200:
                        updated_invoice = response.json()
                        if updated_invoice.get('payment_method') == new_method:
                            self.log_test("Invoice payment method update", True, f"Updated to {new_method}")
                        else:
                            self.log_test("Invoice payment method update", False, 
                                        f"Expected {new_method}, got {updated_invoice.get('payment_method')}")
                else:
                    self.log_test(f"Change payment method {invoice_number}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Payment method change test", False, str(e))
        
        # Test 2: Test same payment method
        try:
            if len(invoices) > 1:
                invoice = invoices[1]
                current_method = invoice.get('payment_method')
                invoice_id = invoice.get('id')
                
                response = self.session.put(
                    f"{BACKEND_URL}/invoices/{invoice_id}/change-payment-method",
                    params={"new_payment_method": current_method}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message = result.get('message', '')
                    if "نفسها" in message or "same" in message.lower():
                        self.log_test("Same payment method handling", True, f"Message: {message}")
                    else:
                        self.log_test("Same payment method handling", False, f"Unexpected message: {message}")
                else:
                    self.log_test("Same payment method handling", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Same payment method test", False, str(e))
        
        # Test 3: Invalid payment method
        try:
            if invoices:
                invoice = invoices[0]
                response = self.session.put(
                    f"{BACKEND_URL}/invoices/{invoice['id']}/change-payment-method",
                    params={"new_payment_method": "طريقة غير صحيحة"}
                )
                
                if response.status_code == 400:
                    self.log_test("Invalid payment method rejection", True, "Correctly rejected")
                else:
                    self.log_test("Invalid payment method rejection", False, 
                                f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid payment method test", False, str(e))
    
    def test_invoice_cancellation_existing(self):
        """Test invoice cancellation with existing invoices"""
        print("\n=== Testing Invoice Cancellation with Existing Invoices ===")
        
        invoices = self.get_existing_invoices()
        if not invoices:
            self.log_test("Invoice cancellation test", False, "No invoices available")
            return
        
        # Test 1: Cancel a non-deferred invoice (treasury reversal)
        try:
            non_deferred_invoice = None
            for invoice in invoices:
                if invoice.get('payment_method') != 'آجل':
                    non_deferred_invoice = invoice
                    break
            
            if non_deferred_invoice:
                invoice_id = non_deferred_invoice['id']
                invoice_number = non_deferred_invoice['invoice_number']
                payment_method = non_deferred_invoice['payment_method']
                amount = non_deferred_invoice.get('total_amount', 0)
                
                print(f"\nTesting cancellation of Invoice {invoice_number} (Method: {payment_method}, Amount: {amount})")
                
                # Get treasury balance before
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
                        response = self.session.delete(f"{BACKEND_URL}/invoices/{invoice_id}/cancel")
                        
                        if response.status_code == 200:
                            result = response.json()
                            self.log_test(f"Cancel invoice {invoice_number}", True, 
                                        f"Treasury reversed: {result.get('treasury_reversed')}")
                            
                            # Verify treasury reversal
                            if result.get('treasury_reversed'):
                                response = self.session.get(f"{BACKEND_URL}/treasury/balances")
                                if response.status_code == 200:
                                    balances_after = response.json()
                                    balance_after = balances_after.get(account_id, 0)
                                    reduction = balance_before - balance_after
                                    
                                    if abs(reduction - amount) < 0.01:
                                        self.log_test("Treasury reversal verification", True, 
                                                    f"Reduced {reduction} from {account_id}")
                                    else:
                                        self.log_test("Treasury reversal verification", False, 
                                                    f"Expected {amount}, actual {reduction}")
                            
                            # Verify invoice deleted
                            response = self.session.get(f"{BACKEND_URL}/invoices/{invoice_id}")
                            if response.status_code == 404:
                                self.log_test("Invoice deletion verification", True, "Invoice deleted")
                            else:
                                self.log_test("Invoice deletion verification", False, 
                                            f"Invoice still exists: {response.status_code}")
                        else:
                            self.log_test(f"Cancel invoice {invoice_number}", False, 
                                        f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_test("Cancel non-deferred invoice", False, "No non-deferred invoice found")
        except Exception as e:
            self.log_test("Invoice cancellation test", False, str(e))
        
        # Test 2: Cancel non-existent invoice
        try:
            response = self.session.delete(f"{BACKEND_URL}/invoices/non-existent-id/cancel")
            
            if response.status_code == 404:
                self.log_test("Cancel non-existent invoice", True, "Correctly returned 404")
            else:
                self.log_test("Cancel non-existent invoice", False, 
                            f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Cancel non-existent invoice test", False, str(e))
    
    def test_treasury_transactions(self):
        """Test treasury transaction creation and consistency"""
        print("\n=== Testing Treasury Transaction Consistency ===")
        
        try:
            # Get all treasury transactions
            response = self.session.get(f"{BACKEND_URL}/treasury/transactions")
            if response.status_code == 200:
                transactions = response.json()
                self.log_test("Get treasury transactions", True, f"Found {len(transactions)} transactions")
                
                # Check for recent transactions related to invoice operations
                recent_transactions = [t for t in transactions if "تحويل" in t.get('description', '') or "إلغاء" in t.get('description', '')]
                if recent_transactions:
                    self.log_test("Invoice-related transactions found", True, 
                                f"Found {len(recent_transactions)} invoice-related transactions")
                    
                    # Show some examples
                    for i, trans in enumerate(recent_transactions[:3]):
                        print(f"   Transaction {i+1}: {trans.get('description')} - {trans.get('amount')} - {trans.get('account_id')}")
                else:
                    self.log_test("Invoice-related transactions found", False, "No invoice-related transactions found")
            else:
                self.log_test("Get treasury transactions", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Treasury transactions test", False, str(e))
        
        # Test treasury balances
        try:
            response = self.session.get(f"{BACKEND_URL}/treasury/balances")
            if response.status_code == 200:
                balances = response.json()
                self.log_test("Get treasury balances", True, "Balances retrieved successfully")
                
                # Show current balances
                for account, balance in balances.items():
                    if isinstance(balance, (int, float)) and balance != 0:
                        print(f"   {account}: {balance}")
            else:
                self.log_test("Get treasury balances", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Treasury balances test", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("FOCUSED INVOICE MANAGEMENT API TEST SUMMARY")
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
        
        return success_rate >= 80
    
    def run_all_tests(self):
        """Run all focused tests"""
        print("Starting Focused Invoice Management API Tests...")
        print("Testing with existing invoices from the database")
        
        self.test_payment_method_change_existing()
        self.test_invoice_cancellation_existing()
        self.test_treasury_transactions()
        
        return self.print_summary()

def main():
    """Main function"""
    tester = FocusedInvoiceTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Focused Invoice Management API tests completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()