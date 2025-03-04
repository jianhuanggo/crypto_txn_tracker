"""
Transaction models for the crypto transaction tracker.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class TransactionType(Enum):
    """Types of cryptocurrency transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PURCHASE = "purchase"
    SALE = "sale"
    TRANSFER = "transfer"
    SWAP = "swap"
    FEE = "fee"
    UNKNOWN = "unknown"


class TransactionSource(Enum):
    """Sources of transaction data."""
    EXCHANGE = "exchange"
    BLOCKCHAIN = "blockchain"
    DEX = "dex"
    MANUAL = "manual"


@dataclass
class Transaction:
    """Base transaction model."""
    id: str
    timestamp: datetime
    transaction_type: TransactionType
    source: TransactionSource
    amount: float
    currency: str
    fee: float = 0.0
    fee_currency: str = ""
    status: str = "completed"
    notes: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    related_transactions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "transaction_type": self.transaction_type.value,
            "source": self.source.value,
            "amount": self.amount,
            "currency": self.currency,
            "fee": self.fee,
            "fee_currency": self.fee_currency,
            "status": self.status,
            "notes": self.notes,
            "raw_data": self.raw_data,
            "related_transactions": self.related_transactions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        # Convert string timestamp to datetime
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        # Convert string enum values to enum types
        if isinstance(data.get("transaction_type"), str):
            data["transaction_type"] = TransactionType(data["transaction_type"])
        
        if isinstance(data.get("source"), str):
            data["source"] = TransactionSource(data["source"])
        
        return cls(**data)
