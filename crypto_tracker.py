#!/usr/bin/env python
"""
Entry point for the crypto transaction tracker.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.interface import main

if __name__ == "__main__":
    main()
