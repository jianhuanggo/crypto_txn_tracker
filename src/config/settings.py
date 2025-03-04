"""
Configuration settings for the crypto transaction tracker.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET", "")

# Blockchain settings
ETH_NODE_URL = os.getenv("ETH_NODE_URL", "https://mainnet.infura.io/v3/")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID", "")

# Database settings (using SQLite for simplicity)
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "transactions.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
