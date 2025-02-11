from crypto_trading_bot import TradingSession
import logging

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Trading configuration
    config = {
        'web3_provider': 'https://sepolia-rollup.arbitrum.io/rpc',
        'keys_file': 'wallet_keys.txt',
        'proxy_file': 'proxies.txt',
        'proxy_type': 'regular',
        'enable_logs': True,
        'enable_shuffling': True,
        'thread_count': 2,  # Start with small number for testing
        'launch_delay': (5, 10),  # Short delays for testing
        'branch_wallet_range': (2, 3),
        'max_parallel_branches': 2,
        'trading_assets': ['BTC', 'ETH', 'SOL'],
        'position_direction': 'random',
        'volume_percentage_range': (10, 50),
        'trades_per_wallet': 2
    }

    # Initialize trading session
    session = TradingSession(config)

    try:
        # Test parallel trading
        logging.info("Starting parallel trading test...")
        session.execute_parallel_trading()
        logging.info("Parallel trading completed")

        # Test branch trading
        logging.info("Starting branch trading test...")
        session.execute_branch_trading()
        logging.info("Branch trading completed")

    except Exception as e:
        logging.error(f"Trading error: {str(e)}")

if __name__ == "__main__":
    main() 