from test_data import TEST_WALLETS, TEST_PROXIES, TEST_CONFIGS, TEST_TRADE_SCENARIOS
from test_utils import setup_test_files, cleanup_test_files
from crypto_trading_bot import TradingSession
import logging
import time

def run_test_scenarios():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='test_scenarios.log'
    )
    
    # Create test files
    setup_test_files(TEST_WALLETS, TEST_PROXIES)
    
    try:
        # 1. Test Parallel Trading
        logging.info("=== Testing Parallel Trading ===")
        parallel_session = TradingSession(TEST_CONFIGS["parallel_trading"])
        
        for scenario in TEST_TRADE_SCENARIOS:
            logging.info(f"\nExecuting scenario: {scenario['name']}")
            wallet = TEST_WALLETS[scenario['wallet_index']]
            
            result = parallel_session._process_wallet_with_size(
                wallet['private_key'],
                scenario['direction'],
                scenario['size']
            )
            
            logging.info(f"Scenario {scenario['name']} result: {result}")
            time.sleep(2)  # Delay between scenarios
        
        # 2. Test Branch Trading
        logging.info("\n=== Testing Branch Trading ===")
        branch_session = TradingSession(TEST_CONFIGS["branch_trading"])
        branch_session.execute_branch_trading()
        
    except Exception as e:
        logging.error(f"Test scenario execution failed: {str(e)}")
    
    finally:
        cleanup_test_files()
        logging.info("Test scenarios completed")

if __name__ == "__main__":
    run_test_scenarios() 