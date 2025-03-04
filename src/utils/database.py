"""
Database utilities for the crypto transaction tracker.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.models.transaction import Transaction


class Database:
    """SQLite database manager for transaction storage."""
    
    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            fee REAL,
            fee_currency TEXT,
            status TEXT,
            notes TEXT,
            raw_data TEXT,
            related_transactions TEXT
        )
        ''')
        
        # Create transaction links table for tracking related transactions
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_links (
            parent_id TEXT,
            child_id TEXT,
            relationship_type TEXT,
            PRIMARY KEY (parent_id, child_id),
            FOREIGN KEY (parent_id) REFERENCES transactions(id),
            FOREIGN KEY (child_id) REFERENCES transactions(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_transaction(self, transaction: Transaction) -> bool:
        """Save a transaction to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO transactions (
                id, timestamp, transaction_type, source, amount, currency,
                fee, fee_currency, status, notes, raw_data, related_transactions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.id,
                transaction.timestamp.isoformat(),
                transaction.transaction_type.value,
                transaction.source.value,
                transaction.amount,
                transaction.currency,
                transaction.fee,
                transaction.fee_currency,
                transaction.status,
                transaction.notes,
                json.dumps(transaction.raw_data),
                json.dumps(transaction.related_transactions)
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False
        finally:
            conn.close()
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Convert row to dict
        data = dict(row)
        data['raw_data'] = json.loads(data['raw_data'])
        data['related_transactions'] = json.loads(data['related_transactions'])
        
        return Transaction.from_dict(data)
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            data = dict(row)
            data['raw_data'] = json.loads(data['raw_data'])
            data['related_transactions'] = json.loads(data['related_transactions'])
            transactions.append(Transaction.from_dict(data))
        
        return transactions
    
    def link_transactions(self, parent_id: str, child_id: str, relationship_type: str) -> bool:
        """Link two transactions together."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO transaction_links (parent_id, child_id, relationship_type)
            VALUES (?, ?, ?)
            ''', (parent_id, child_id, relationship_type))
            
            # Update related_transactions field in parent transaction
            parent = self.get_transaction(parent_id)
            if parent and child_id not in parent.related_transactions:
                parent.related_transactions.append(child_id)
                self.save_transaction(parent)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error linking transactions: {e}")
            return False
        finally:
            conn.close()
    
    def get_transaction_chain(self, transaction_id: str) -> List[Transaction]:
        """Get a chain of related transactions starting from the given transaction ID."""
        # Get the initial transaction
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return []
        
        # Initialize the chain with the starting transaction
        chain = [transaction]
        visited = {transaction_id}
        
        # Get all related transactions recursively
        self._get_related_transactions(transaction_id, chain, visited)
        
        # Sort by timestamp
        chain.sort(key=lambda t: t.timestamp)
        
        return chain
    
    def _get_related_transactions(self, transaction_id: str, chain: List[Transaction], visited: set):
        """Recursively get related transactions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get child transactions
        cursor.execute('''
        SELECT child_id FROM transaction_links WHERE parent_id = ?
        ''', (transaction_id,))
        
        child_ids = [row['child_id'] for row in cursor.fetchall()]
        
        # Get parent transactions
        cursor.execute('''
        SELECT parent_id FROM transaction_links WHERE child_id = ?
        ''', (transaction_id,))
        
        parent_ids = [row['parent_id'] for row in cursor.fetchall()]
        
        conn.close()
        
        # Process all related transactions
        for related_id in child_ids + parent_ids:
            if related_id not in visited:
                visited.add(related_id)
                related_tx = self.get_transaction(related_id)
                if related_tx:
                    chain.append(related_tx)
                    self._get_related_transactions(related_id, chain, visited)
