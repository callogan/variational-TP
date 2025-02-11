"""Test suite for crypto trading functionality"""

import unittest
from unittest.mock import patch, MagicMock
import time
from typing import Dict
import logging

# Import test data and utilities
from test_data import (
    TEST_WALLETS, 
    TEST_PROXIES, 
    TEST_CONFIGS, 
    TEST_TRADE_SCENARIOS
)
from test_utils import setup_test_files, cleanup_test_files

# Import main trading code
from crypto_trading_bot import WalletManager, ProxyManager, TransactionManager, TradingSession

class TestWalletManager(unittest.TestCase):
    def setUp(self):
        setup_test_files(TEST_WALLETS, TEST_PROXIES)
        self.wallet_manager = WalletManager("test_wallet_keys.txt")
        logging.info("WalletManager initialized.")
    
    def tearDown(self):
        cleanup_test_files()
    
    def test_load_wallets(self):
        """Test wallet loading functionality"""
        self.assertEqual(len(self.wallet_manager.wallets), len(TEST_WALLETS))
        logging.info("Wallet loading test passed.")
    
    def test_add_wallet(self):
        """Test adding new wallet"""
        new_wallet = "0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef"
        self.wallet_manager.add_wallet(new_wallet)
        self.assertIn(new_wallet, self.wallet_manager.wallets)
        logging.info("Wallet addition test passed.")

class TestProxyManager(unittest.TestCase):
    def setUp(self):
        setup_test_files(TEST_WALLETS, TEST_PROXIES)
        self.proxy_manager_regular = ProxyManager("test_proxies.txt", "regular")
        self.proxy_manager_mobile = ProxyManager("test_proxies.txt", "mobile")
        logging.info("ProxyManager initialized.")
    
    def tearDown(self):
        cleanup_test_files()
    
    def test_load_proxies(self):
        """Test proxy loading functionality"""
        self.assertEqual(len(self.proxy_manager_regular.proxies), len(TEST_PROXIES))
        logging.info("Proxy loading test passed.")
    
    def test_get_regular_proxy(self):
        """Test regular proxy assignment"""
        proxy = self.proxy_manager_regular.get_proxy(0)
        self.assertIn("ip_port", proxy)
        self.assertIn("auth", proxy)
        logging.info("Regular proxy assignment test passed.")
    
    @patch('requests.get')
    def test_get_mobile_proxy(self, mock_get):
        """Test mobile proxy with refresh"""
        proxy = self.proxy_manager_mobile.get_proxy(1)
        self.assertIn("refresh_link", proxy)
        mock_get.assert_called_once()
        logging.info("Mobile proxy refresh test passed.")

class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self.transaction_manager = TransactionManager()
        logging.info("TransactionManager initialized.")
    
    def test_random_user_agent(self):
        """Test random user agent generation"""
        user_agent = self.transaction_manager.get_random_user_agent()
        self.assertIn(user_agent, self.transaction_manager.user_agents)
        logging.info("Random user agent test passed.")
    
    def test_generate_signature(self):
        """Test transaction signature generation"""
        private_key = TEST_WALLETS[0]["private_key"]
        message = "test_message"
        signature = self.transaction_manager._generate_signature(private_key, message)
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0)
        logging.info("Signature generation test passed.")
    
    def test_execute_trade(self):
        """Test trade execution"""
        result = self.transaction_manager.execute_trade(
            TEST_WALLETS[0]["private_key"],
            "BTC",
            "long",
            1000,
            {"ip_port": "192.168.1.1:8080", "auth": "user1:pass1"}
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("transaction_hash", result)
        self.assertIn("signature", result)
        self.assertIn("details", result)
        logging.info("Trade execution test passed.")

class TestTradingSession(unittest.TestCase):
    def setUp(self):
        setup_test_files(TEST_WALLETS, TEST_PROXIES)
        self.parallel_session = TradingSession(TEST_CONFIGS["parallel_trading"])
        self.branch_session = TradingSession(TEST_CONFIGS["branch_trading"])
        logging.info("TradingSession initialized.")
    
    def tearDown(self):
        cleanup_test_files()
    
    def test_parallel_trading(self):
        """Test parallel trading execution"""
        with patch.object(time, 'sleep'):  # Skip delays in testing
            self.parallel_session.execute_parallel_trading()
            logging.info("Parallel trading executed.")
    
    def test_branch_trading(self):
        """Test branch trading execution"""
        with patch.object(time, 'sleep'):  # Skip delays in testing
            self.branch_session.execute_branch_trading()
            logging.info("Branch trading executed.")
    
    def test_trade_scenarios(self):
        """Test various trading scenarios"""
        for scenario in TEST_TRADE_SCENARIOS:
            with self.subTest(scenario=scenario["name"]):
                result = self.parallel_session._process_wallet_with_size(
                    TEST_WALLETS[scenario["wallet_index"]]["private_key"],
                    scenario["direction"],
                    scenario["size"]
                )
                self.assertEqual(result["status"], scenario["expected_result"])
                logging.info(f"Trade scenario '{scenario['name']}' executed with result: {result}")

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests() 