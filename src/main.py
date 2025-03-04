"""
Main application for the crypto transaction tracker.
"""
import os
import sys
from typing import List, Dict, Any, Optional

from src.blockchain.ethereum import EthereumClient
from src.exchange.coinbase import CoinbaseClient
from src.models.transaction import Transaction
from src.utils.database import Database
from src.config.settings import DATABASE_PATH


class CryptoTracker:
    """Main application class for tracking crypto transactions."""
    
    def __init__(self):
        """Initialize the crypto tracker."""
        self.db = Database(DATABASE_PATH)
        self.eth_client = EthereumClient()
        self.coinbase_client = CoinbaseClient()
    
    def track_ethereum_address(self, address: str) -> List[Transaction]:
        """Track transactions for an Ethereum address."""
        transactions = self.eth_client.get_address_transactions(address)
        
        # Save transactions to database
        for tx in transactions:
            self.db.save_transaction(tx)
        
        return transactions
    
    def track_coinbase_account(self) -> List[Transaction]:
        """Track transactions from Coinbase account."""
        try:
            transactions = self.coinbase_client.get_all_transactions()
            
            # Save transactions to database
            for tx in transactions:
                self.db.save_transaction(tx)
            
            return transactions
        except ValueError as e:
            print(f"Error: {e}")
            return []
    
    def get_transaction_history(self) -> List[Transaction]:
        """Get all tracked transactions."""
        return self.db.get_all_transactions()
    
    def get_transaction_chain(self, transaction_id: str) -> List[Transaction]:
        """Get a chain of related transactions."""
        return self.db.get_transaction_chain(transaction_id)
    
    def link_transactions(self, parent_id: str, child_id: str, relationship_type: str = "continuation") -> bool:
        """Link two transactions as part of the same flow."""
        return self.db.link_transactions(parent_id, child_id, relationship_type)
