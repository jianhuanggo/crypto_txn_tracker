"""
DEX (Decentralized Exchange) tracking module for the crypto transaction tracker.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from web3 import Web3
from web3.exceptions import TransactionNotFound

from src.models.transaction import Transaction, TransactionType, TransactionSource
from src.blockchain.ethereum import EthereumClient


class DEXTracker:
    """Tracker for DEX transactions."""
    
    # Common DEX contract addresses
    DEX_CONTRACTS = {
        "uniswap_v2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    }
    
    def __init__(self, eth_client: Optional[EthereumClient] = None):
        """Initialize DEX tracker."""
        self.eth_client = eth_client or EthereumClient()
        self.web3 = self.eth_client.web3
    
    def is_dex_transaction(self, tx_hash: str) -> bool:
        """Check if a transaction is a DEX transaction."""
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            if not tx or not tx.get('to'):
                return False
            
            # Check if the transaction is to a known DEX contract
            return tx['to'].lower() in [addr.lower() for addr in self.DEX_CONTRACTS.values()]
        except TransactionNotFound:
            return False
        except Exception as e:
            print(f"Error checking if transaction is DEX: {e}")
            return False
    
    def track_dex_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Track a DEX transaction."""
        try:
            # First, get the basic transaction details
            tx = self.eth_client.get_transaction(tx_hash)
            if not tx:
                return None
            
            # If it's not a DEX transaction, return the basic transaction
            if not self.is_dex_transaction(tx_hash):
                return tx
            
            # Enhance the transaction with DEX-specific information
            tx.transaction_type = TransactionType.SWAP
            tx.notes = f"DEX Swap - {tx.notes}"
            
            # Try to decode the input data to get more details about the swap
            # This is a simplified version and would need to be expanded for production use
            input_data = tx.raw_data.get('input', '')
            if input_data and len(input_data) > 10:
                # The first 10 characters (including '0x') are the function signature
                function_sig = input_data[:10]
                
                # Common function signatures for swaps
                swap_sigs = {
                    "0x38ed1739": "swapExactTokensForTokens",
                    "0x7ff36ab5": "swapExactETHForTokens",
                    "0x4a25d94a": "swapTokensForExactETH",
                    "0x18cbafe5": "swapExactTokensForETH",
                    "0x5c11d795": "swapExactTokensForTokensSupportingFeeOnTransferTokens"
                }
                
                if function_sig in swap_sigs:
                    tx.notes = f"DEX Swap - {swap_sigs[function_sig]} - {tx.notes}"
            
            return tx
        except Exception as e:
            print(f"Error tracking DEX transaction: {e}")
            return None
    
    def find_dex_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Transaction]:
        """Find DEX transactions for an address."""
        # Get all transactions for the address
        transactions = self.eth_client.get_address_transactions(address, start_block, end_block)
        
        # Filter for DEX transactions
        dex_transactions = []
        for tx in transactions:
            if self.is_dex_transaction(tx.id):
                dex_tx = self.track_dex_transaction(tx.id)
                if dex_tx:
                    dex_transactions.append(dex_tx)
        
        return dex_transactions
