"""
Coinbase exchange interface for the crypto transaction tracker.
"""
import hmac
import hashlib
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import requests

from src.models.transaction import Transaction, TransactionType, TransactionSource
from src.config.settings import COINBASE_API_KEY, COINBASE_API_SECRET


class CoinbaseClient:
    """Client for interacting with the Coinbase API."""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """Initialize Coinbase client."""
        self.api_key = api_key or COINBASE_API_KEY
        self.api_secret = api_secret or COINBASE_API_SECRET
        self.base_url = "https://api.coinbase.com/v2"
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """Generate signature for Coinbase API request."""
        message = timestamp + method + request_path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make a request to the Coinbase API."""
        if not self.api_key or not self.api_secret:
            raise ValueError("Coinbase API key and secret are required")
        
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))
        
        headers = {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-VERSION": "2021-04-29",
            "Content-Type": "application/json"
        }
        
        body = ""
        if data:
            body = json.dumps(data)
        
        signature = self._generate_signature(timestamp, method, endpoint, body)
        headers["CB-ACCESS-SIGN"] = signature
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=body
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {"data": []}
    
    def get_accounts(self) -> List[Dict]:
        """Get all accounts."""
        response = self._request("GET", "/accounts")
        return response.get("data", [])
    
    def get_transactions(self, account_id: str) -> List[Transaction]:
        """Get transactions for an account."""
        endpoint = f"/accounts/{account_id}/transactions"
        response = self._request("GET", endpoint)
        
        transactions = []
        for tx_data in response.get("data", []):
            # Map Coinbase transaction type to our transaction type
            tx_type_map = {
                "buy": TransactionType.PURCHASE,
                "sell": TransactionType.SALE,
                "send": TransactionType.WITHDRAWAL,
                "receive": TransactionType.DEPOSIT,
                "exchange": TransactionType.SWAP,
                "fiat_deposit": TransactionType.DEPOSIT,
                "fiat_withdrawal": TransactionType.WITHDRAWAL,
                "fee": TransactionType.FEE
            }
            
            tx_type = tx_type_map.get(tx_data.get("type"), TransactionType.UNKNOWN)
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(tx_data.get("created_at").replace("Z", "+00:00"))
            
            # Get amount and currency
            amount = float(tx_data.get("amount", {}).get("amount", 0))
            currency = tx_data.get("amount", {}).get("currency", "")
            
            # Get native amount (USD equivalent)
            native_amount = float(tx_data.get("native_amount", {}).get("amount", 0))
            native_currency = tx_data.get("native_amount", {}).get("currency", "USD")
            
            transaction = Transaction(
                id=tx_data.get("id", str(uuid.uuid4())),
                timestamp=timestamp,
                transaction_type=tx_type,
                source=TransactionSource.EXCHANGE,
                amount=amount,
                currency=currency,
                fee=0.0,  # Coinbase doesn't expose fees directly in transaction data
                fee_currency=currency,
                status=tx_data.get("status", "completed"),
                notes=tx_data.get("details", {}).get("title", ""),
                raw_data={
                    "coinbase_id": tx_data.get("id"),
                    "type": tx_data.get("type"),
                    "status": tx_data.get("status"),
                    "amount": tx_data.get("amount"),
                    "native_amount": tx_data.get("native_amount"),
                    "description": tx_data.get("details", {}).get("subtitle", ""),
                    "created_at": tx_data.get("created_at"),
                    "updated_at": tx_data.get("updated_at"),
                    "resource": tx_data.get("resource"),
                    "resource_path": tx_data.get("resource_path")
                }
            )
            
            transactions.append(transaction)
        
        return transactions
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get transactions for all accounts."""
        accounts = self.get_accounts()
        all_transactions = []
        
        for account in accounts:
            account_id = account.get("id")
            transactions = self.get_transactions(account_id)
            all_transactions.extend(transactions)
        
        # Sort by timestamp
        all_transactions.sort(key=lambda t: t.timestamp)
        
        return all_transactions
