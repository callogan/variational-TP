from test_data import TEST_WALLETS
from crypto_trading_bot import WalletManager
import logging

def test_wallet_operations():
    logging.basicConfig(level=logging.INFO)
    
    # Create test wallet file
    with open("test_wallet_keys.txt", "w") as f:
        for wallet in TEST_WALLETS:
            f.write(f"{wallet['private_key']}\n")
    
    # Initialize wallet manager
    wallet_manager = WalletManager("test_wallet_keys.txt")
    
    # Test operations
    print(f"Loaded wallets: {len(wallet_manager.wallets)}")
    for wallet in wallet_manager.wallets:
        print(f"Wallet: {wallet[:10]}...")

if __name__ == "__main__":
    test_wallet_operations() 