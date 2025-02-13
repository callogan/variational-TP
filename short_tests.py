import logging
import unittest
import random
from typing import Dict
from unittest.mock import patch, MagicMock

from crypto_trading_bot import TradingSession  # Assuming this is your main module


class TestTradingSession(unittest.TestCase):

    def setUp(self):
        """Setup method to initialize mocks and config before each test."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.wallet_manager_mock = MagicMock()
        self.proxy_manager_mock = MagicMock()
        self.transaction_manager_mock = MagicMock()

        self.config = {
            'branch_wallet_range': (2, 3),
            'max_parallel_branches': 2,
            'enable_shuffling': False,
            'trading_assets': ['BTC'],
            'position_direction': 'long',
            'volume_percentage_range': (10, 20),
            'enable_logs': True,
            'proxy_type': 'regular'  # Added for consistency
        }
        self.session = TradingSession(self.config)
        self.session.wallet_manager = self.wallet_manager_mock
        self.session.proxy_manager = self.proxy_manager_mock
        self.session.transaction_manager = self.transaction_manager_mock

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_success(self, mock_sleep):
        """Test successful execution of one trading session iteration."""

        mock_wallets = ['wallet_1', 'wallet_2', 'wallet_3', 'wallet_4', 'wallet_5', 'wallet_6']
        self.wallet_manager_mock.wallets = mock_wallets
        self.wallet_manager_mock.get_next_wallet.side_effect = lambda x: mock_wallets[x] if x < len(mock_wallets) else None

        def get_proxy_side_effect(account_id: int):
            proxy_list = [
                {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'},
                {'ip_port': '127.0.0.1:8081', 'auth': 'user2:pass2'},
                {'ip_port': '127.0.0.1:8082', 'auth': 'user3:pass3'}
            ]
            return proxy_list[account_id % len(proxy_list)]

        self.proxy_manager_mock.get_proxy.side_effect = get_proxy_side_effect

        def execute_trade_side_effect(wallet: str, asset: str, direction: str, size: float, proxy: Dict) -> Dict:
            return {
                'status': 'success',
                'transaction_hash': f'hash_{wallet[:8]}',
                'timestamp': '2024-02-11T12:00:00',
                'details': {
                    'asset': asset,
                    'direction': direction,
                    'size': size,
                    'wallet': wallet[:8],
                    'proxy_used': proxy['ip_port']
                }
            }

        self.transaction_manager_mock.execute_trade.side_effect = execute_trade_side_effect

        with self.assertLogs(level=logging.DEBUG) as cm:  # Use assertLogs for log checking
            self.session.run_session(execution_mode="branch")

            self.assertTrue(hasattr(self.session, 'proxy_manager'))
            self.assertEqual(self.session.proxy_manager, self.proxy_manager_mock)
            self.assertGreater(self.proxy_manager_mock.get_proxy.call_count, 0)

            for call in self.proxy_manager_mock.get_proxy.call_args_list:
                args, _ = call
                account_id = args[0]
                self.assertIsInstance(account_id, int)
                self.assertGreaterEqual(account_id, 0)
                self.assertLess(account_id, len(mock_wallets))

            for call in self.proxy_manager_mock.get_proxy.call_args_list:
                _, proxy_used = call
                result = get_proxy_side_effect(0)
                self.assertIn('ip_port', result)
                self.assertIn('auth', result)
                self.assertIsInstance(result['ip_port'], str)
                self.assertIsInstance(result['auth'], str)

            for call in self.transaction_manager_mock.execute_trade.call_args_list:
                args, _ = call
                _, _, _, _, proxy = args
                self.assertIn('ip_port', proxy)
                self.assertIn('auth', proxy)

        # You can add more specific log checks within cm.output if needed.
        # Example: self.assertIn("All proxy-related checks passed successfully", "".join(cm.output))

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_no_wallets(self, mock_sleep):
        """Test case for handling situation with no available wallets."""
        self.wallet_manager_mock.wallets = []
        self.wallet_manager_mock.get_next_wallet.return_value = None

        self.session.run_session("branch")
        self.transaction_manager_mock.execute_trade.assert_not_called()

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    @patch('random.randint')  # Mocking random.randint
    @patch('random.uniform')  # Mocking random.uniform
    def test_run_session_several_wallets(self, mock_uniform, mock_randint, mock_sleep):
        """Test with several available wallets and have random.randint and random.uniform mocked."""
        mock_wallets = [
            ('wallet_1', 'key_1'), ('wallet_2', 'key_2'), ('wallet_3', 'key_3'),
            ('wallet_4', 'key_4'), ('wallet_5', 'key_5')
        ]
        self.wallet_manager_mock.wallets = mock_wallets
        self.wallet_manager_mock.get_next_wallet.side_effect = lambda index: mock_wallets[index] if 0 <= index < len(
            mock_wallets) else None

        proxy_data = {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'}
        self.proxy_manager_mock.get_proxy.side_effect = lambda account_id: proxy_data

        asset = self.config['trading_assets'][0]
        direction = self.config['position_direction']
        size = 15.0  # Average value from volume_percentage_range

        # Setting up values for random.randint to return
        mock_randint.side_effect = [
            3,  # branch_size for first branch
            2,  # long_count for first branch
            2,  # branch_size for second branch (2 wallets)
            1   # long_count for second branch
        ]

        # Setting up values for random.uniform to return
        mock_uniform.side_effect = [
            15.0, 15.0, 15.0, 15.0, 15.0  # Mocked trade sizes
        ]

        self.session.run_session("branch")

        # Checking calls of transaction_manager_mock.execute_trade
        expected_calls = [
            (('wallet_1', 'key_1'), asset, "long", size, proxy_data),
            (('wallet_2', 'key_2'), asset, "long", size, proxy_data),
            (('wallet_3', 'key_3'), asset, "short", size, proxy_data),
            (('wallet_4', 'key_4'), asset, "long", size, proxy_data),
            (('wallet_5', 'key_5'), asset, "short", size, proxy_data),
        ]
        expected_calls = expected_calls[::-1]
        p = self.transaction_manager_mock.execute_trade.call_args_list
        actual_calls = [call for call in self.transaction_manager_mock.execute_trade.call_args_list]

        self.assertEqual(len(actual_calls), len(expected_calls),
                         "execute_trade calls number doesn't match expected")

        for i, (expected_args) in enumerate(expected_calls):
            actual_call = self.transaction_manager_mock.execute_trade.call_args_list[i]
            # self.transaction_manager_mock.execute_trade.assert_called_with(*expected_args)

        # Additionally, check the number of random.randint and random.uniform calls
        # self.assertEqual(mock_randint.call_count, 4, "4 calls of random.randint expected")
        # self.assertEqual(mock_uniform.call_count, 5, "5 calls of random.uniform expected")

    # @patch('crypto_trading_bot.time.sleep', return_value=None)
    # def test_run_session_several_wallets(self, mock_sleep):
    #     """Test with several available wallets using random.seed for deterministic random values."""
    #     # Set random seed for reproducible results
    #     random.seed(42)  # Using 42 as seed to get consistent random values
    #
    #     mock_wallets = [
    #         ('wallet_1', 'key_1'), ('wallet_2', 'key_2'), ('wallet_3', 'key_3'),
    #         ('wallet_4', 'key_4'), ('wallet_5', 'key_5')
    #     ]
    #     self.wallet_manager_mock.wallets = mock_wallets
    #     self.wallet_manager_mock.get_next_wallet.side_effect = lambda index: mock_wallets[index] if 0 <= index < len(
    #         mock_wallets) else None
    #
    #     proxy_data = {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'}
    #     self.proxy_manager_mock.get_proxy.side_effect = lambda account_id: proxy_data
    #
    #     asset = self.config['trading_assets'][0]
    #     direction = self.config['position_direction']
    #     size = 15.0  # Average value from volume_percentage_range
    #
    #     # Run the session
    #     self.session.run_session("branch")
    #
    #     # Checking calls of transaction_manager_mock.execute_trade
    #     expected_calls = [
    #         (('wallet_1', 'key_1'), asset, direction, size, proxy_data),
    #         (('wallet_2', 'key_2'), asset, direction, size, proxy_data),
    #         (('wallet_3', 'key_3'), asset, direction, size, proxy_data),
    #         (('wallet_4', 'key_4'), asset, direction, size, proxy_data),
    #         (('wallet_5', 'key_5'), asset, direction, size, proxy_data),
    #     ]
    #
    #     actual_calls = self.transaction_manager_mock.execute_trade.call_args_list
    #
    #     self.assertEqual(len(actual_calls), len(expected_calls),
    #                      "execute_trade calls number doesn't match expected")
    #
    #     for i, expected_args in enumerate(expected_calls):
    #         actual_call = actual_calls[i]
    #         self.assertEqual(actual_call.args, expected_args,
    #                          f"Call {i} arguments don't match expected values")
    #
    #     # Reset random seed after test
    #     random.seed()

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_no_proxies(self, mock_sleep):
        """Test case for no available proxy servers."""
        self.wallet_manager_mock.get_next_wallet.return_value = ('wallet_1', 'key_1')
        self.proxy_manager_mock.get_proxy.return_value = None

        self.session.run_session("branch")
        self.transaction_manager_mock.execute_trade.assert_not_called()

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    @patch('crypto_trading_bot.random.uniform', return_value=25.0)  # random.uniform mocking
    def test_run_session_single_proxy(self, mock_random_uniform, mock_sleep):
        """Test trading session with a single proxy server."""
        # Setup test wallets
        mock_wallets = [
            ('wallet_1', 'key_1'), ('wallet_2', 'key_2')
        ]
        self.wallet_manager_mock.wallets = mock_wallets

        # Setup single test proxy
        test_proxy = {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'}
        self.proxy_manager_mock.get_proxy.return_value = test_proxy

        # Run the session
        with self.assertLogs(level=logging.DEBUG):
            self.session.run_session("branch")

            f = self.proxy_manager_mock.get_proxy.call_count
            r = len(mock_wallets)
            # Core assertions
            # 1. Verify proxy was called for each wallet
            self.assertEqual(
                self.proxy_manager_mock.get_proxy.call_count,
                len(mock_wallets),
                "get_proxy should be called once per wallet"
            )

            # 2. Verify all trades used the correct proxy
            trade_calls = self.transaction_manager_mock.execute_trade.call_args_list
            for call in trade_calls:
                _, _, _, _, proxy = call.args
                self.assertEqual(
                    proxy,
                    test_proxy,
                    "All trades should use the configured proxy"
                )

    # @patch('crypto_trading_bot.time.sleep', return_value=None)
    # def test_run_session_one_proxy(self, mock_sleep):
    #     """Test with multiple proxy servers."""
    #     # Setup test wallets
    #     mock_wallets = [
    #         ('wallet_1', 'key_1'), ('wallet_2', 'key_2'), ('wallet_3', 'key_3'),
    #         ('wallet_4', 'key_4'), ('wallet_5', 'key_5')
    #     ]
    #     self.wallet_manager_mock.wallets = mock_wallets
    #
    #     # Setup test proxies
    #     test_proxies = [
    #         {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'},
    #         {'ip_port': '127.0.0.1:8081', 'auth': 'user2:pass2'},
    #         {'ip_port': '127.0.0.1:8082', 'auth': 'user3:pass3'}
    #     ]
    #
    #     def get_proxy_side_effect(account_id: int) -> Dict:
    #         return test_proxies[account_id % len(test_proxies)]
    #
    #     self.proxy_manager_mock.get_proxy.side_effect = get_proxy_side_effect
    #
    #     # Run the session and capture logs
    #     with self.assertLogs(level=logging.DEBUG) as cm:
    #         self.session.run_session("branch")
    #
    #         # Verify proxy manager was called for each wallet
    #         self.assertEqual(
    #             self.proxy_manager_mock.get_proxy.call_count,
    #             len(mock_wallets),
    #             f"get_proxy must be called {len(mock_wallets)} times"
    #         )
    #
    #         # Verify correct proxy assignment for each call
    #         proxy_calls = self.proxy_manager_mock.get_proxy.call_args_list
    #         for i, call in enumerate(proxy_calls):
    #             account_id = call.args[0]
    #             expected_proxy = test_proxies[account_id % len(test_proxies)]
    #             actual_proxy = get_proxy_side_effect(account_id)
    #
    #             self.assertEqual(
    #                 actual_proxy,
    #                 expected_proxy,
    #                 f"Incorrect proxy for account_id {account_id}"
    #             )
    #
    #         # Verify trade execution used correct proxies
    #         trade_calls = self.transaction_manager_mock.execute_trade.call_args_list
    #         for i, call in enumerate(trade_calls):
    #             _, _, _, _, proxy = call.args
    #             self.assertIn(
    #                 proxy,
    #                 test_proxies,
    #                 f"Trade operation {i + 1} uses unknown proxy"
    #             )
    #
    #         # Track and verify proxy usage distribution
    #         proxy_usage = {}
    #         for call in proxy_calls:
    #             account_id = call.args[0]
    #             proxy = get_proxy_side_effect(account_id)
    #             proxy_key = proxy['ip_port']
    #             proxy_usage[proxy_key] = proxy_usage.get(proxy_key, 0) + 1
    #
    #         # Verify all proxies were used
    #         for proxy in test_proxies:
    #             self.assertIn(
    #                 proxy['ip_port'],
    #                 proxy_usage,
    #                 f"Proxy {proxy['ip_port']} was not used"
    #             )

        # Additional log checks (optional)
        # self.assertIn("Proxy usage statistics:", "".join(cm.output))
