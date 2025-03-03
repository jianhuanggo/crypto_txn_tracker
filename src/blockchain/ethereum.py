"""
Ethereum blockchain interface for the crypto transaction tracker.
"""
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

import requests
from web3 import Web3

from src.models.transaction import Transaction, TransactionType, TransactionSource
from src.config.settings import ETHERSCAN_API_KEY, ETH_NODE_URL, INFURA_PROJECT_ID


class EthereumClient:
    """Client for interacting with the Ethereum blockchain."""
    
    def __init__(self, api_key: str = None, node_url: str = None, infura_id: str = None):
        """Initialize Ethereum client."""
        self.api_key = api_key or ETHERSCAN_API_KEY
        
        # Set up Web3 connection
        if node_url and 'infura.io' in node_url and infura_id:
            self.web3 = Web3(Web3.HTTPProvider(f"{node_url}{infura_id}"))
        elif node_url:
            self.web3 = Web3(Web3.HTTPProvider(node_url))
        elif ETH_NODE_URL and INFURA_PROJECT_ID:
            self.web3 = Web3(Web3.HTTPProvider(f"{ETH_NODE_URL}{INFURA_PROJECT_ID}"))
        else:
            # Fallback to public node
            self.web3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))
        
        self.etherscan_base_url = "https://api.etherscan.io/api"
    
    def is_connected(self) -> bool:
        """Check if connected to Ethereum node."""
        return self.web3.is_connected()
    
    def get_eth_balance(self, address: str) -> float:
        """Get ETH balance for an address."""
        try:
            balance_wei = self.web3.eth.get_balance(address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return 0.0
    
    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction details by hash."""
        try:
            # Get transaction from Web3
            tx = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if not tx or not receipt:
                return None
            
            # Get block timestamp
            block = self.web3.eth.get_block(tx['blockNumber'])
            timestamp = datetime.fromtimestamp(block['timestamp'])
            
            # Determine transaction type
            tx_type = TransactionType.TRANSFER
            
            # Calculate value in ETH
            value_eth = float(self.web3.from_wei(tx['value'], 'ether'))
            
            # Calculate gas fee
            gas_price_wei = tx['gasPrice']
            gas_used = receipt['gasUsed']
            gas_fee_wei = gas_price_wei * gas_used
            gas_fee_eth = float(self.web3.from_wei(gas_fee_wei, 'ether'))
            
            # Create transaction object
            transaction = Transaction(
                id=tx_hash,
                timestamp=timestamp,
                transaction_type=tx_type,
                source=TransactionSource.BLOCKCHAIN,
                amount=value_eth,
                currency="ETH",
                fee=gas_fee_eth,
                fee_currency="ETH",
                status="confirmed" if receipt['status'] == 1 else "failed",
                notes=f"From: {tx['from']}, To: {tx['to']}",
                raw_data={
                    "from": tx['from'],
                    "to": tx['to'],
                    "blockNumber": tx['blockNumber'],
                    "gasPrice": str(tx['gasPrice']),
                    "gasUsed": gas_used,
                    "nonce": tx['nonce'],
                    "input": tx['input'],
                    "value": str(tx['value']),
                    "receipt": {
                        "status": receipt['status'],
                        "logs": [dict(log) for log in receipt['logs']]
                    }
                }
            )
            
            return transaction
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None
    
    def get_address_transactions(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Transaction]:
        """Get transactions for an address using Etherscan API."""
        if not self.api_key:
            print("Etherscan API key not provided")
            return []
        
        transactions = []
        
        # Get normal transactions
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.etherscan_base_url, params=params)
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                for tx_data in data["result"]:
                    # Create transaction object
                    timestamp = datetime.fromtimestamp(int(tx_data["timeStamp"]))
                    value_eth = float(self.web3.from_wei(int(tx_data["value"]), 'ether'))
                    gas_price_wei = int(tx_data["gasPrice"])
                    gas_used = int(tx_data["gasUsed"])
                    gas_fee_eth = float(self.web3.from_wei(gas_price_wei * gas_used, 'ether'))
                    
                    # Determine transaction type
                    if address.lower() == tx_data["from"].lower():
                        tx_type = TransactionType.WITHDRAWAL
                    else:
                        tx_type = TransactionType.DEPOSIT
                    
                    transaction = Transaction(
                        id=tx_data["hash"],
                        timestamp=timestamp,
                        transaction_type=tx_type,
                        source=TransactionSource.BLOCKCHAIN,
                        amount=value_eth,
                        currency="ETH",
                        fee=gas_fee_eth,
                        fee_currency="ETH",
                        status="confirmed" if tx_data["txreceipt_status"] == "1" else "failed",
                        notes=f"From: {tx_data['from']}, To: {tx_data['to']}",
                        raw_data=tx_data
                    )
                    
                    transactions.append(transaction)
            
            # Add a delay to avoid rate limiting
            time.sleep(0.2)
            
            # Get internal transactions
            params["action"] = "txlistinternal"
            response = requests.get(self.etherscan_base_url, params=params)
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                for tx_data in data["result"]:
                    # Create transaction object for internal transactions
                    timestamp = datetime.fromtimestamp(int(tx_data["timeStamp"]))
                    value_eth = float(self.web3.from_wei(int(tx_data["value"]), 'ether'))
                    
                    # Determine transaction type
                    if address.lower() == tx_data["from"].lower():
                        tx_type = TransactionType.WITHDRAWAL
                    else:
                        tx_type = TransactionType.DEPOSIT
                    
                    transaction = Transaction(
                        id=f"{tx_data['hash']}_{tx_data.get('traceId', uuid.uuid4().hex)}",
                        timestamp=timestamp,
                        transaction_type=tx_type,
                        source=TransactionSource.BLOCKCHAIN,
                        amount=value_eth,
                        currency="ETH",
                        fee=0.0,  # Internal transactions don't have separate fees
                        fee_currency="ETH",
                        status="confirmed",  # Internal transactions are always from confirmed txs
                        notes=f"Internal Transaction - From: {tx_data['from']}, To: {tx_data['to']}",
                        raw_data=tx_data
                    )
                    
                    transactions.append(transaction)
            
            # Sort transactions by timestamp
            transactions.sort(key=lambda t: t.timestamp)
            
            return transactions
        
        except Exception as e:
            print(f"Error getting address transactions: {e}")
            return []
