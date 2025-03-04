# Crypto Transaction Tracker

A production-grade Python system to track cryptocurrency transactions across exchanges and blockchains.

## Features

- Track on-chain Ethereum transactions
- Track off-chain transactions from Coinbase
- Track DEX transactions
- Link related transactions to view the complete lifecycle
- Command-line interface for easy interaction

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jianhuanggo/crypto_txn_tracker.git
cd crypto_txn_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```bash
cp .env.template .env
# Edit .env with your API keys
```

## Usage

```bash
# Track Ethereum address transactions
./crypto_tracker.py track-eth 0x123456789abcdef123456789abcdef123456789

# Track Coinbase account transactions
./crypto_tracker.py track-coinbase

# List tracked transactions
./crypto_tracker.py list --limit 20 --currency ETH

# Show transaction details
./crypto_tracker.py show <transaction_id>

# Show transaction chain
./crypto_tracker.py chain <transaction_id>

# Link related transactions
./crypto_tracker.py link <parent_transaction_id> <child_transaction_id>
```

## Documentation

- [API Documentation](docs/api_documentation.md)
- [API Key Guide](docs/api_key_guide.md)
- [Test Results](docs/test_results.md)
