# Payment Processor - Payment Service
import sqlite3
from typing import Dict, Any, Optional
from decimal import Decimal

class PaymentProcessor:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
    
    def process_payment(self, user_id: str, amount: float) -> bool:
        """Process payment - ISSUE: SQL Injection vulnerability"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # CRITICAL: SQL Injection vulnerability
            query = f"INSERT INTO transactions (user_id, amount) VALUES ('{user_id}', {amount})"
            cursor.execute(query)
            conn.commit()
            return True
        except:  # ISSUE: Bare except
            pass
        finally:
            conn.close()
        return False
    
    def process_refund(self, transaction_id: str) -> bool:
        """Process refund - ISSUE: Race condition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # ISSUE: Race condition - check and refund not atomic
            cursor.execute(f"SELECT amount FROM transactions WHERE id = {transaction_id}")
            result = cursor.fetchone()
            
            if result:
                amount = result[0]
                # ISSUE: Another transaction could refund between check and update
                cursor.execute(f"UPDATE transactions SET refunded = 1 WHERE id = {transaction_id}")
                cursor.execute(f"INSERT INTO refunds (transaction_id, amount) VALUES ({transaction_id}, {amount})")
                conn.commit()
                return True
        except:  # ISSUE: Bare except
            pass
        finally:
            conn.close()
        return False
    
    def get_balance(self, user_id: str) -> Optional[Decimal]:
        """Get user balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT SUM(amount) FROM transactions WHERE user_id = '{user_id}'")
            result = cursor.fetchone()
            return Decimal(result[0]) if result and result[0] else Decimal(0)
        except:
            pass
        finally:
            conn.close()
        return None
