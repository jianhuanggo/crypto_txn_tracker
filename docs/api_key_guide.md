# Guide to Obtaining API Keys for Crypto Transaction Tracker

This guide provides step-by-step instructions for obtaining the API keys required by the Crypto Transaction Tracker system.

## Why API Keys Are Necessary

The Crypto Transaction Tracker uses external APIs to fetch transaction data from:

1. **Etherscan**: For on-chain Ethereum transactions
2. **Coinbase**: For exchange transactions

These services require API keys for authentication, rate limiting, and usage tracking. Without these keys, the system will not be able to fetch transaction data from these sources.

## Etherscan API Key

Etherscan provides an API for accessing Ethereum blockchain data. Here's how to obtain an API key:

1. **Create an Etherscan Account**:
   - Go to [https://etherscan.io/register](https://etherscan.io/register)
   - Fill in the registration form and submit
   - Verify your email address

2. **Generate an API Key**:
   - Log in to your Etherscan account
   - Navigate to your profile by clicking on your username in the top-right corner
   - Select "API Keys" from the dropdown menu
   - Click "Add" to create a new API key
   - Enter a name for your API key (e.g., "Crypto Tracker")
   - Click "Create New API Key"

3. **Copy Your API Key**:
   - Your new API key will be displayed on the screen
   - Copy this key and add it to your `.env` file as `ETHERSCAN_API_KEY=your_key_here`

## Coinbase API Key

Coinbase provides an API for accessing your exchange account data. Here's how to obtain API keys:

1. **Create a Coinbase Account** (if you don't already have one):
   - Go to [https://www.coinbase.com/signup](https://www.coinbase.com/signup)
   - Follow the registration process
   - Verify your identity as required

2. **Generate API Keys**:
   - Log in to your Coinbase account
   - Go to Settings > API
   - Click "New API Key"
   - Select the accounts you want to grant access to
   - Set permissions (for this application, you only need "view" permissions)
   - You may need to complete two-factor authentication
   - Set an optional IP whitelist for added security

3. **Copy Your API Key and Secret**:
   - Your API key and secret will be displayed
   - Copy both the API key and secret
   - Add them to your `.env` file as:
     ```
     COINBASE_API_KEY=your_key_here
     COINBASE_API_SECRET=your_secret_here
     ```

## Infura Project ID (Optional)

For more reliable Ethereum node access, you can use Infura:

1. **Create an Infura Account**:
   - Go to [https://infura.io/register](https://infura.io/register)
   - Fill in the registration form and submit
   - Verify your email address

2. **Create a New Project**:
   - Log in to your Infura dashboard
   - Click "Create New Project"
   - Select "Ethereum" as the project type
   - Enter a name for your project (e.g., "Crypto Tracker")

3. **Copy Your Project ID**:
   - Your project ID will be displayed on the project settings page
   - Copy this ID and add it to your `.env` file as `INFURA_PROJECT_ID=your_id_here`

## Setting Up Your Environment

After obtaining the necessary API keys, you need to add them to your environment:

1. **Create a `.env` File**:
   - In the root directory of the Crypto Transaction Tracker, create a file named `.env`
   - Add your API keys to this file:
     ```
     ETHERSCAN_API_KEY=your_etherscan_key
     COINBASE_API_KEY=your_coinbase_key
     COINBASE_API_SECRET=your_coinbase_secret
     INFURA_PROJECT_ID=your_infura_id
     ```

2. **Test Your Configuration**:
   - Run the Crypto Transaction Tracker with a test command to verify that your API keys are working correctly:
     ```
     ./crypto_tracker.py track-eth 0xYourEthereumAddress
     ```

## API Key Security

Keep your API keys secure:

1. **Never share your API keys** or commit them to public repositories
2. **Use environment variables** instead of hardcoding keys in your code
3. **Set appropriate permissions** for your API keys (read-only when possible)
4. **Regularly rotate your API keys** for enhanced security
5. **Set IP restrictions** when available to limit access to your keys

## Troubleshooting

If you encounter issues with your API keys:

1. **Verify the keys are correct** and properly formatted in your `.env` file
2. **Check rate limits** to ensure you haven't exceeded the allowed number of requests
3. **Confirm account status** to ensure your accounts are in good standing
4. **Check for API service outages** on the provider's status page
