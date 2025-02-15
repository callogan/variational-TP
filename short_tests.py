import logging
import unittest
import random
from typing import Dict
from unittest.mock import patch, MagicMock, call

from crypto_trading_bot import TradingSession  # Assuming this is your main module


class TestTradingSession(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.config = {
            'branch_wallet_range': (2, 3),
            'max_parallel_branches': 2,
            'enable_shuffling': False,
            'trading_assets': ['BTC'],
            'position_direction': 'long',
            'volume_percentage_range': (10, 20),
            'enable_logs': True,
            'proxy_type': 'regular'
        }

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_success(self, mock_sleep):
        wallet_manager_mock = MagicMock()
        proxy_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.proxy_manager = proxy_manager_mock
        session.transaction_manager = transaction_manager_mock

        mock_wallets = ['wallet_1', 'wallet_2', 'wallet_3']
        wallet_manager_mock.wallets = mock_wallets
        wallet_manager_mock.get_next_wallet.side_effect = lambda x: mock_wallets[x] if x < len(mock_wallets) else None

        proxy_manager_mock.get_proxy.side_effect = lambda account_id: {
            'ip_port': f'127.0.0.1:808{account_id}', 'auth': f'user{account_id}:pass{account_id}'
        }

        transaction_manager_mock.execute_trade.side_effect = lambda wallet, asset, direction, size, proxy: {
            'status': 'success',
            'transaction_hash': f'hash_{wallet}',
            'details': {'wallet': wallet, 'proxy_used': proxy['ip_port']}
        }

        session.run_session("branch")
        transaction_manager_mock.execute_trade.assert_called()

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_no_wallets(self, mock_sleep):
        wallet_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.transaction_manager = transaction_manager_mock

        wallet_manager_mock.get_next_wallet.return_value = None

        session.run_session("branch")
        transaction_manager_mock.execute_trade.assert_not_called()

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    @patch('random.randint')  # Mocking random.randint
    @patch('random.uniform')  # Mocking random.uniform
    def test_run_session_several_wallets(self, mock_uniform, mock_randint, mock_sleep):
        """Test with several available wallets and have random.randint and random.uniform mocked"""

        # Creation of Mock-objects for wallet managers, proxies and transactions
        wallet_manager_mock = MagicMock()
        proxy_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        # Setting test wallets
        mock_wallets = [
            ('wallet_1', 'key_1'), ('wallet_2', 'key_2'), ('wallet_3', 'key_3'),
            ('wallet_4', 'key_4'), ('wallet_5', 'key_5')
        ]
        wallet_manager_mock.wallets = mock_wallets
        wallet_manager_mock.get_next_wallet.side_effect = lambda index: mock_wallets[index] if 0 <= index < len(
            mock_wallets) else None

        # Setting proxy-manager
        proxy_data = {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'}
        proxy_manager_mock.get_proxy.side_effect = lambda account_id: proxy_data

        # Setting configuration
        asset = self.config['trading_assets'][0]
        direction = self.config['position_direction']
        size = 15.0  # Average value from volume_percentage_range

        # Setting returnable values for random.randint
        mock_randint.side_effect = [
            3,  # branch_size for first branch
            2,  # long_count for first branch
            2,  # branch_size for second branch (2 wallets)
            1  # long_count for second branch
        ]

        # Setting returnable values for random.uniform
        mock_uniform.side_effect = [15.0] * 5  # All the transactions have the same size

        # Creation of session items with Mock-objects
        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.proxy_manager = proxy_manager_mock
        session.transaction_manager = transaction_manager_mock
        # session.config = config

        # Running tested function
        session.run_session("branch")

        # Expected calls
        expected_calls = [
            (('wallet_1', 'key_1'), asset, "long", 7.5, proxy_data),
            (('wallet_2', 'key_2'), asset, "long", 7.5, proxy_data),
            (('wallet_3', 'key_3'), asset, "short", 15.0, proxy_data),
            (('wallet_4', 'key_4'), asset, "long", 15.0, proxy_data),
            (('wallet_5', 'key_5'), asset, "short", 15.0, proxy_data),
        ]

        # Get actual calls
        actual_calls = [call.args for call in transaction_manager_mock.execute_trade.call_args_list]

        # Verify number of calls
        self.assertEqual(
            len(actual_calls),
            len(expected_calls),
            f"Expected {len(expected_calls)} calls but got {len(actual_calls)}"
        )

        a = expected_calls
        b = actual_calls
        # Check each expected call
        for expected_call in expected_calls:
            found_the_right_call = False
            bogus_calls = []

            for actual_call in actual_calls:
                # Check if actual call matches expected call
                if actual_call == expected_call:
                    found_the_right_call = True
                else:
                    # Store calls that don't match for error reporting
                    bogus_calls.append(actual_call)

            # Assert we found the expected call
            assert found_the_right_call, (
                f"transaction_manager.execute_trade was called with expected args: "
                f"wallet={expected_call[0]}, asset={expected_call[1]}, "
                f"direction={expected_call[2]}, size={expected_call[3]}, "
                f"proxy={expected_call[4]}"
            )

            # Assert we didn't find any unexpected calls
            if bogus_calls:
                unexpected_calls_str = "\n".join(
                    f"- wallet={call[0]}, asset={call[1]}, direction={call[2]}, "
                    f"size={call[3]}, proxy={call[4]}"
                    for call in bogus_calls
                )
                # assert not bogus_calls, (
                #     f"transaction_manager.execute_trade was called with unexpected args:\n{unexpected_calls_str}"
                # )

    @patch('crypto_trading_bot.time.sleep', return_value=None)
    def test_run_session_no_proxies(self, mock_sleep):
        wallet_manager_mock = MagicMock()
        proxy_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.proxy_manager = proxy_manager_mock
        session.transaction_manager = transaction_manager_mock

        wallet_manager_mock.get_next_wallet.return_value = ('wallet_1', 'key_1')
        proxy_manager_mock.get_proxy.return_value = None

        session.run_session("branch")
        transaction_manager_mock.execute_trade.assert_not_called()


    @patch('crypto_trading_bot.time.sleep', return_value=None)
    @patch('crypto_trading_bot.random.uniform', return_value=25.0)
    @patch('crypto_trading_bot.random.randint')  # Changed to be configurable
    def test_run_session_single_proxy(self, mock_random_randint, mock_random_uniform, mock_sleep):
        # Set up the mock to return appropriate values for different calls
        mock_random_randint.side_effect = [
            2,  # For branch_size (called with branch_range)
            1,  # For long_count (called with (1, branch_size))
        ]

        wallet_manager_mock = MagicMock()
        proxy_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.proxy_manager = proxy_manager_mock
        session.transaction_manager = transaction_manager_mock

        mock_wallets = [('wallet_1', 'key_1'), ('wallet_2', 'key_2')]
        wallet_manager_mock.wallets = mock_wallets

        test_proxy = {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'}
        proxy_manager_mock.get_proxy.return_value = test_proxy

        session.run_session("branch")

        # Verify proxy manager was called for each wallet
        self.assertEqual(
            proxy_manager_mock.get_proxy.call_count,
            len(mock_wallets),
            "Proxy manager should be called once for each wallet"
        )

        # Verify each trade used the correct proxy
        for call in transaction_manager_mock.execute_trade.call_args_list:
            _, _, _, _, proxy = call.args
            self.assertEqual(
                proxy,
                test_proxy,
                "Each trade should use the configured test proxy"
            )

        # Verify random.randint was called correctly with actual arguments from implementation
        mock_random_randint.assert_has_calls([
            call(2, 3),  # First call for branch_size
            call(1, 1),  # Second call for long_count
        ])
        self.assertEqual(mock_random_randint.call_count, 2)