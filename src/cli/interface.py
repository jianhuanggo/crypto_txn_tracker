"""
Command-line interface for the crypto transaction tracker.
"""
import argparse
import sys
from datetime import datetime
from typing import List, Optional
from tabulate import tabulate

from src.main import CryptoTracker
from src.models.transaction import Transaction


class CLI:
    """Command-line interface for the crypto transaction tracker."""
    
    def __init__(self):
        """Initialize CLI."""
        self.tracker = CryptoTracker()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Crypto Transaction Tracker - Track cryptocurrency transactions across exchanges and blockchains"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # Track Ethereum address
        track_eth_parser = subparsers.add_parser("track-eth", help="Track Ethereum address transactions")
        track_eth_parser.add_argument("address", help="Ethereum address to track")
        
        # Track Coinbase account
        track_coinbase_parser = subparsers.add_parser("track-coinbase", help="Track Coinbase account transactions")
        
        # List transactions
        list_parser = subparsers.add_parser("list", help="List tracked transactions")
        list_parser.add_argument("--limit", type=int, default=10, help="Limit number of transactions to show")
        list_parser.add_argument("--currency", help="Filter by currency")
        list_parser.add_argument("--type", help="Filter by transaction type")
        list_parser.add_argument("--source", help="Filter by transaction source")
        
        # Show transaction details
        show_parser = subparsers.add_parser("show", help="Show transaction details")
        show_parser.add_argument("id", help="Transaction ID")
        
        # Show transaction chain
        chain_parser = subparsers.add_parser("chain", help="Show transaction chain")
        chain_parser.add_argument("id", help="Starting transaction ID")
        
        # Link transactions
        link_parser = subparsers.add_parser("link", help="Link two transactions")
        link_parser.add_argument("parent", help="Parent transaction ID")
        link_parser.add_argument("child", help="Child transaction ID")
        link_parser.add_argument("--type", default="continuation", help="Relationship type")
        
        return parser
    
    def _format_transactions(self, transactions: List[Transaction]) -> str:
        """Format transactions for display."""
        if not transactions:
            return "No transactions found."
        
        table_data = []
        for tx in transactions:
            table_data.append([
                tx.id[:8] + "...",  # Truncate ID for display
                tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                tx.transaction_type.value,
                tx.source.value,
                f"{tx.amount:.8f} {tx.currency}",
                f"{tx.fee:.8f} {tx.fee_currency}" if tx.fee > 0 else "-",
                tx.status
            ])
        
        headers = ["ID", "Timestamp", "Type", "Source", "Amount", "Fee", "Status"]
        return tabulate(table_data, headers=headers, tablefmt="grid")
    
    def _format_transaction_details(self, transaction: Transaction) -> str:
        """Format transaction details for display."""
        if not transaction:
            return "Transaction not found."
        
        details = [
            ["ID", transaction.id],
            ["Timestamp", transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
            ["Type", transaction.transaction_type.value],
            ["Source", transaction.source.value],
            ["Amount", f"{transaction.amount:.8f} {transaction.currency}"],
            ["Fee", f"{transaction.fee:.8f} {transaction.fee_currency}" if transaction.fee > 0 else "-"],
            ["Status", transaction.status],
            ["Notes", transaction.notes]
        ]
        
        if transaction.related_transactions:
            related_txs = ", ".join([tx_id[:8] + "..." for tx_id in transaction.related_transactions])
            details.append(["Related Transactions", related_txs])
        
        return tabulate(details, tablefmt="grid")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI with arguments."""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        try:
            if args.command == "track-eth":
                print(f"Tracking Ethereum address: {args.address}")
                transactions = self.tracker.track_ethereum_address(args.address)
                print(f"Found {len(transactions)} transactions.")
                print(self._format_transactions(transactions[:10]))
                return 0
            
            elif args.command == "track-coinbase":
                print("Tracking Coinbase account...")
                transactions = self.tracker.track_coinbase_account()
                print(f"Found {len(transactions)} transactions.")
                print(self._format_transactions(transactions[:10]))
                return 0
            
            elif args.command == "list":
                transactions = self.tracker.get_transaction_history()
                
                # Apply filters
                if args.currency:
                    transactions = [tx for tx in transactions if tx.currency.lower() == args.currency.lower()]
                
                if args.type:
                    transactions = [tx for tx in transactions if tx.transaction_type.value.lower() == args.type.lower()]
                
                if args.source:
                    transactions = [tx for tx in transactions if tx.source.value.lower() == args.source.lower()]
                
                # Apply limit
                transactions = transactions[:args.limit]
                
                print(self._format_transactions(transactions))
                return 0
            
            elif args.command == "show":
                transaction = self.tracker.db.get_transaction(args.id)
                print(self._format_transaction_details(transaction))
                return 0
            
            elif args.command == "chain":
                chain = self.tracker.get_transaction_chain(args.id)
                print(f"Transaction chain (length: {len(chain)}):")
                print(self._format_transactions(chain))
                return 0
            
            elif args.command == "link":
                success = self.tracker.link_transactions(args.parent, args.child, args.type)
                if success:
                    print(f"Successfully linked transactions {args.parent} and {args.child}.")
                else:
                    print("Failed to link transactions.")
                    return 1
                return 0
            
            else:
                print(f"Unknown command: {args.command}")
                self.parser.print_help()
                return 1
        
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main entry point for CLI."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
