import unittest
from unittest.mock import patch
import logging
import time

from crypto_trading_bot import TradingSession
from test_data import TEST_WALLETS, TEST_PROXIES, TEST_CONFIGS
from test_utils import setup_test_files, cleanup_test_files

class TestTradingFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='trading_test.log'
        )
        setup_test_files(TEST_WALLETS, TEST_PROXIES)
        cls.session = TradingSession(TEST_CONFIGS["parallel_trading"])
        logging.info("Trading session initialized for functionality tests.")

    @classmethod
    def tearDownClass(cls):
        """Cleanup test environment"""
        cleanup_test_files()

    def test_1_wallet_initialization(self):
        """Test if wallets are properly loaded"""
        self.assertEqual(
            len(self.session.wallet_manager.wallets),
            len(TEST_WALLETS)
        )
        logging.info("Wallet initialization test passed.")

    def test_2_proxy_setup(self):
        """Test if proxies are properly configured"""
        self.assertEqual(
            len(self.session.proxy_manager.proxies),
            len(TEST_PROXIES)
        )
        logging.info("Proxy setup test passed.")

    @patch.object(time, 'sleep')  # Skip delays in testing
    def test_3_single_trade_execution(self, mock_sleep):
        """Test single trade execution"""
        wallet_key = TEST_WALLETS[0]["private_key"]
        result = self.session._process_wallet_with_size(
            wallet_key,
            "long",
            1000
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("transaction_hash", result)
        self.assertIn("signature", result)
        logging.info(f"Single trade execution test passed: {result}")

    @patch.object(time, 'sleep')  # Skip delays in testing
    def test_4_parallel_trading(self, mock_sleep):
        """Test parallel trading execution"""
        try:
            self.session.execute_parallel_trading()
            logging.info("Parallel trading test passed.")
            self.assertTrue(True)
        except Exception as e:
            logging.error(f"Parallel trading test failed: {str(e)}")
            self.fail(f"Parallel trading failed: {str(e)}")

    @patch.object(time, 'sleep')  # Skip delays in testing
    def test_5_branch_trading(self, mock_sleep):
        """Test branch trading execution"""
        try:
            self.session.execute_branch_trading()
            logging.info("Branch trading test passed.")
            self.assertTrue(True)
        except Exception as e:
            logging.error(f"Branch trading test failed: {str(e)}")
            self.fail(f"Branch trading failed: {str(e)}")

def run_functionality_tests():
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_functionality_tests() 