"""Utility functions for testing"""

import os
from typing import List, Dict

def setup_test_files(wallets: List[Dict], proxies: List[str]):
    """Create test wallet and proxy files"""
    # Create test wallet keys file
    with open("test_wallet_keys.txt", "w") as f:
        for wallet in wallets:
            f.write(f"{wallet['private_key']}\n")
    
    # Create test proxies file
    with open("test_proxies.txt", "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def cleanup_test_files():
    """Remove test files"""
    files_to_remove = ["test_wallet_keys.txt", "test_proxies.txt"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file) 