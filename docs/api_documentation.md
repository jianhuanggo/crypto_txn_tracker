# API Documentation for Crypto Transaction Tracker

This document outlines the APIs used in the Crypto Transaction Tracker system and how they are integrated to track the complete lifecycle of cryptocurrency transactions.

## Ethereum Blockchain APIs

### Etherscan API

The Etherscan API is used to track on-chain Ethereum transactions.

#### Key Features:
- Track transactions for a specific Ethereum address
- Get transaction details including value, gas fees, and status
- Track internal transactions (contract interactions)
- Historical transaction data

#### Authentication:
- Requires an API key from [Etherscan](https://etherscan.io/register)
- Free tier allows 5 requests per second, up to 100,000 requests per day

#### Key Endpoints:

1. **Get Normal Transactions by Address**
   ```
   https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&sort=asc&apikey={apikey}
   ```

2. **Get Internal Transactions by Address**
   ```
   https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&startblock={startblock}&endblock={endblock}&sort=asc&apikey={apikey}
   ```

3. **Get ERC-20 Token Transfer Events by Address**
   ```
   https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock={startblock}&endblock={endblock}&sort=asc&apikey={apikey}
   ```

### Web3.py

Web3.py is a Python library for interacting with the Ethereum blockchain.

#### Key Features:
- Connect to Ethereum nodes (local or remote)
- Get transaction details
- Get block information
- Interact with smart contracts

#### Authentication:
- Requires an Ethereum node URL (e.g., Infura, Alchemy, or local node)
- For Infura, requires a project ID

#### Key Methods:

1. **Get Transaction**
   ```python
   web3.eth.get_transaction(tx_hash)
   ```

2. **Get Transaction Receipt**
   ```python
   web3.eth.get_transaction_receipt(tx_hash)
   ```

3. **Get Balance**
   ```python
   web3.eth.get_balance(address)
   ```

## Exchange APIs

### Coinbase API

The Coinbase API is used to track off-chain transactions on the Coinbase exchange.

#### Key Features:
- Get account balances
- Get transaction history
- Track deposits, withdrawals, buys, and sells
- Track conversions between currencies

#### Authentication:
- Requires API key and secret from Coinbase
- Uses HMAC SHA-256 signatures for authentication

#### Key Endpoints:

1. **List Accounts**
   ```
   GET https://api.coinbase.com/v2/accounts
   ```

2. **Get Account**
   ```
   GET https://api.coinbase.com/v2/accounts/{account_id}
   ```

3. **List Transactions**
   ```
   GET https://api.coinbase.com/v2/accounts/{account_id}/transactions
   ```

## Decentralized Exchange (DEX) APIs

For tracking transactions on decentralized exchanges, we need to monitor blockchain events and interpret them.

### Ethereum DEX Transactions

DEX transactions on Ethereum can be tracked by:

1. Monitoring token transfer events (ERC-20 transfers)
2. Identifying transactions to DEX contract addresses
3. Decoding transaction input data to understand the swap details

#### Common DEX Contract Addresses:
- Uniswap V2 Router: 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
- Uniswap V3 Router: 0xE592427A0AEce92De3Edee1F18E0157C05861564
- SushiSwap Router: 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F

## Tracking Transaction Lifecycle

To track the complete lifecycle of a transaction across different platforms:

1. **Deposit Fiat to Exchange**
   - Use Coinbase API to track fiat deposits
   - Store transaction details in the database

2. **Purchase Crypto on Exchange**
   - Use Coinbase API to track buy orders
   - Link to the original deposit transaction

3. **Withdraw Crypto to Wallet**
   - Use Coinbase API to track withdrawals
   - Use Etherscan API to track the on-chain transaction
   - Link the exchange withdrawal to the blockchain transaction

4. **Transfer to DEX**
   - Use Etherscan API to track the transfer to a DEX contract
   - Decode the transaction input to understand the swap details
   - Link to the previous transaction

5. **Swap on DEX**
   - Track token transfer events to identify the tokens received
   - Link to the DEX transfer transaction

## API Integration in the System

The Crypto Transaction Tracker integrates these APIs through the following components:

1. **EthereumClient** (`src/blockchain/ethereum.py`)
   - Connects to Ethereum blockchain using Web3.py
   - Uses Etherscan API for historical transaction data
   - Parses and normalizes blockchain data into Transaction objects

2. **CoinbaseClient** (`src/exchange/coinbase.py`)
   - Connects to Coinbase API
   - Authenticates using API key and secret
   - Retrieves and normalizes exchange data into Transaction objects

3. **Database** (`src/utils/database.py`)
   - Stores all transactions in a SQLite database
   - Maintains relationships between transactions
   - Allows querying for transaction chains

4. **CryptoTracker** (`src/main.py`)
   - Coordinates between different data sources
   - Provides methods to track addresses and accounts
   - Allows linking related transactions

## Rate Limits and Production Considerations

### Etherscan API
- Free tier: 5 requests/second, 100,000 requests/day
- Consider implementing rate limiting and caching
- For production use with high volume, consider a paid plan

### Coinbase API
- Rate limits vary by endpoint
- Implement exponential backoff for retries
- Cache frequently accessed data

### Web3 Providers
- Infura free tier: 100,000 requests/day
- Alchemy free tier: 300M compute units/month
- For production, consider dedicated nodes or paid plans
