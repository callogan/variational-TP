from test_data import TEST_PROXIES
from crypto_trading_bot import ProxyManager
import logging

def test_proxy_operations():
    logging.basicConfig(level=logging.INFO)
    
    # Create test proxy file
    with open("test_proxies.txt", "w") as f:
        for proxy in TEST_PROXIES:
            f.write(f"{proxy}\n")
    
    # Test regular proxies
    proxy_manager = ProxyManager("test_proxies.txt", "regular")
    print("\nTesting regular proxies:")
    for i in range(3):
        proxy = proxy_manager.get_proxy(i)
        print(f"Account {i} proxy: {proxy}")
    
    # Test mobile proxies
    proxy_manager = ProxyManager("test_proxies.txt", "mobile")
    print("\nTesting mobile proxies:")
    for i in range(3):
        proxy = proxy_manager.get_proxy(i)
        print(f"Account {i} proxy: {proxy}")

if __name__ == "__main__":
    test_proxy_operations() 