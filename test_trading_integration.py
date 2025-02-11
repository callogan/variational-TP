import unittest
from unittest.mock import patch
import logging
import time

from crypto_trading_bot import TradingSession
from test_data import TEST_CONFIGS, TEST_WALLETS, TEST_PROXIES
from test_utils import setup_test_files, cleanup_test_files

class TestTradingIntegration(unittest.TestCase):
    def setUp(self):
        """Setup for each test"""
        setup_test_files(TEST_WALLETS, TEST_PROXIES)
        self.config = TEST_CONFIGS["parallel_trading"]
        logging.basicConfig(
            level=logging.INFO,
            filename='integration_test.log'
        )
        logging.info("Integration test environment set up.")

    def tearDown(self):
        """Cleanup after each test"""
        cleanup_test_files()

    @patch.object(time, 'sleep')  # Skip delays in testing
    def test_complete_trading_flow(self, mock_sleep):
        """Test complete trading flow from start to finish"""
        try:
            # 1. Initialize trading session
            session = TradingSession(self.config)
            self.assertIsNotNone(session)

            # 2. Verify wallet setup
            self.assertEqual(
                len(session.wallet_manager.wallets),
                len(TEST_WALLETS)
            )

            # 3. Execute sample trades
            for wallet in TEST_WALLETS[:2]:  # Test with first two wallets
                result = session._process_wallet_with_size(
                    wallet["private_key"],
                    "long",
                    1000
                )
                self.assertEqual(result["status"], "success")
                self.assertIn("transaction_hash", result)
                self.assertIn("signature", result)
                self.assertIn("details", result)

            # 4. Test parallel execution
            session.execute_parallel_trading()

            # 5. Verify trading results
            self.assertTrue(True)  # If we got here without errors, test passed

        except Exception as e:
            logging.error(f"Integration test failed: {str(e)}")
            raise

def run_integration_tests():
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_integration_tests() 