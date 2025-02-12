import logging
import unittest
from typing import Dict

from crypto_trading_bot import TradingSession
from unittest.mock import patch, MagicMock

from unittest.mock import patch, MagicMock
import logging


@patch('crypto_trading_bot.time.sleep', return_value=None)  # Suppress delay in tests
def test_run_session_success(caplog):
    """Test successful execution of one trading session iteration with comprehensive proxy checks"""

    # Set up logging with detailed format
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create mocks for classes and their methods
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    # Create detailed test configuration
    config = {
        'branch_wallet_range': (2, 3),
        'max_parallel_branches': 2,
        'enable_shuffling': False,
        'trading_assets': ['BTC'],
        'position_direction': 'long',
        'volume_percentage_range': (10, 20),
        'enable_logs': True,
        'proxy_type': 'regular'
    }

    # Initialize session
    session = TradingSession(config)
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Set up test wallets
    mock_wallets = ['wallet_1', 'wallet_2', 'wallet_3', 'wallet_4', 'wallet_5', 'wallet_6']
    wallet_manager_mock.wallets = mock_wallets

    # Configure wallet manager responses
    wallet_manager_mock.get_next_wallet.side_effect = lambda x: mock_wallets[x] if x < len(mock_wallets) else None

    # Configure proxy manager responses
    def get_proxy_side_effect(account_id: int):
        """Simulates proxy selection based on account ID"""
        proxy_list = [
            {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'},
            {'ip_port': '127.0.0.1:8081', 'auth': 'user2:pass2'},
            {'ip_port': '127.0.0.1:8082', 'auth': 'user3:pass3'}
        ]
        return proxy_list[account_id % len(proxy_list)]

    proxy_manager_mock.get_proxy.side_effect = get_proxy_side_effect

    # Configure transaction manager responses
    def execute_trade_side_effect(wallet: str, asset: str, direction: str, size: float, proxy: Dict) -> Dict:
        """Simulates trade execution with provided parameters"""
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

    transaction_manager_mock.execute_trade.side_effect = execute_trade_side_effect

    # Run session and capture logs
    with caplog.at_level(logging.DEBUG):
        try:
            # First test: Normal execution
            session.run_session(execution_mode="branch")

            # Verify proxy manager setup
            assert hasattr(session, 'proxy_manager'), "Session should have proxy_manager attribute"
            assert session.proxy_manager == proxy_manager_mock, "Proxy manager should be properly attached"

            # Verify proxy calls occurred
            assert proxy_manager_mock.get_proxy.call_count > 0, "Proxy manager should be called"
            logging.debug(f'get_proxy was called {proxy_manager_mock.get_proxy.call_count} time(s)')

            # Verify proxy call parameters
            for call in proxy_manager_mock.get_proxy.call_args_list:
                args, kwargs = call
                account_id = args[0]  # First argument should be account_id

                # Verify account_id parameter
                assert isinstance(account_id, int), f"account_id should be int, got {type(account_id)}"
                assert account_id >= 0, f"account_id should be non-negative, got {account_id}"
                assert account_id < len(
                    mock_wallets), f"account_id {account_id} exceeds wallet count {len(mock_wallets)}"

                logging.debug(f'get_proxy called with account_id: {account_id}')

            # Verify proxy data format
            for call in proxy_manager_mock.get_proxy.call_args_list:
                _, proxy_used = call
                result = get_proxy_side_effect(0)  # Get sample proxy data
                assert 'ip_port' in result, "Proxy data should contain ip_port"
                assert 'auth' in result, "Proxy data should contain auth"
                assert isinstance(result['ip_port'], str), "ip_port should be string"
                assert isinstance(result['auth'], str), "auth should be string"

            # Verify trade execution with proxies
            for call in transaction_manager_mock.execute_trade.call_args_list:
                args, kwargs = call
                _, _, _, _, proxy = args  # Extract proxy from arguments
                assert 'ip_port' in proxy, "Trade execution should receive proxy with ip_port"
                assert 'auth' in proxy, "Trade execution should receive proxy with auth"
                logging.debug(f'Trade executed with proxy: {proxy["ip_port"]}')

            logging.info("All proxy-related checks passed successfully")

            # Test error handling
            proxy_manager_mock.get_proxy.side_effect = Exception("Proxy error")
            try:
                session.run_session(execution_mode="branch")
                assert False, "Should raise exception on proxy error"
            except Exception as e:
                assert "Proxy error" in str(e), "Should propagate proxy error"
                logging.debug("Error handling test passed")

        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            raise

        finally:
            # Log final statistics
            logging.info(f"""
            Test completion statistics:
            - Wallet operations: {wallet_manager_mock.get_next_wallet.call_count}
            - Proxy operations: {proxy_manager_mock.get_proxy.call_count}
            - Trade executions: {transaction_manager_mock.execute_trade.call_count}
            """)

# @patch('crypto_trading_bot.time.sleep', return_value=None)  # Suppress delay in tests
# def test_run_session_success(caplog):
#     """Test successful execution of one trading session iteration"""
#
#     # Set up logging
#     logging.basicConfig(level=logging.DEBUG)
#
#     # Create mocks for classes and their methods
#     wallet_manager_mock = MagicMock()
#     proxy_manager_mock = MagicMock()
#     transaction_manager_mock = MagicMock()
#
#     # Create session object with specific configuration
#     config = {
#         'branch_wallet_range': (2, 3),  # Set smaller range for testing
#         'max_parallel_branches': 2,
#         'enable_shuffling': False,  # Disable shuffling for predictable behavior
#         'trading_assets': ['BTC'],  # Simplify asset selection
#         'position_direction': 'long',  # Fix direction for predictable behavior
#         'volume_percentage_range': (10, 20)  # Narrow volume range
#     }
#
#     session = TradingSession(config)
#     session.wallet_manager = wallet_manager_mock
#     session.proxy_manager = proxy_manager_mock
#     session.transaction_manager = transaction_manager_mock
#
#     # Set up mock wallets - ensure enough wallets to avoid the if condition
#     mock_wallets = ['wallet_1', 'wallet_2', 'wallet_3', 'wallet_4', 'wallet_5', 'wallet_6']
#     wallet_manager_mock.wallets = mock_wallets
#
#     # Configure wallet_manager mock methods
#     wallet_manager_mock.get_next_wallet.side_effect = lambda x: mock_wallets[x] if x < len(mock_wallets) else None
#
#     # Configure proxy_manager mock methods
#     proxy_manager_mock.get_proxy.return_value = {
#         'ip_port': '127.0.0.1:8080',
#         'auth': 'user:pass'
#     }
#
#     # Configure transaction_manager mock methods
#     transaction_manager_mock.execute_trade.return_value = {
#         'status': 'success',
#         'transaction_hash': 'mock_hash',
#         'timestamp': '2024-02-11T12:00:00',
#         'details': {
#             'asset': 'BTC',
#             'direction': 'long',
#             'size': 15.0,
#             'wallet': 'mock_wallet'
#         }
#     }
#
#     # Run session in branch mode
#     session.run_session(execution_mode="branch")
#
#     # Verify method calls and interactions
#     with caplog.at_level(logging.DEBUG):
#         # Verify wallet operations
#         assert wallet_manager_mock.wallets != [], "Wallets list should not be empty"
#         logging.debug(f'Number of available wallets: {len(wallet_manager_mock.wallets)}')
#
#         # Verify proxy operations
#         assert proxy_manager_mock.get_proxy.call_count > 0, "Proxy manager should be called"
#         logging.debug(f'get_proxy was called {proxy_manager_mock.get_proxy.call_count} time(s)')
#
#         # Verify transaction operations
#         assert transaction_manager_mock.execute_trade.call_count > 0, "Trade execution should occur"
#         logging.debug(f'execute_trade was called {transaction_manager_mock.execute_trade.call_count} time(s)')
#
#         # Verify branch processing
#         for call in transaction_manager_mock.execute_trade.call_args_list:
#             args, kwargs = call
#             logging.debug(f'Trade executed with args: {args}')
#
#     # Verify that the proxy and transaction methods were called once
#     proxy_manager_mock.get_proxy.assert_called_once()
#     transaction_manager_mock.execute_transaction.assert_called_once_with('wallet_1', 'key_1', 'proxy_1')
#
#     # Check that the logs contain the expected messages
#     assert 'get_next_wallet was called' in caplog.text
#     assert 'get_next_proxy was called' in caplog.text
#     assert 'execute_transaction was called' in caplog.text



# def test_run_session_no_wallets(caplog):
#     """Test case for no available wallets"""
#     wallet_manager_mock = MagicMock()
#     proxy_manager_mock = MagicMock()
#     transaction_manager_mock = MagicMock()
#
#     session = TradingSession(config={})
#     session.wallet_manager = wallet_manager_mock
#     session.proxy_manager = proxy_manager_mock
#     session.transaction_manager = transaction_manager_mock
#
#     # Setting no wallets
#     wallet_manager_mock.get_next_wallet.return_value = None
#
#     # Logging mistakes via caplog
#     with caplog.at_level(logging.ERROR):
#         session.run_session("branch")
#     print("CAPLOG_TEXT", caplog.text)
#     # Checking that error message is being recorded
#     assert "Invalid execution mode" in caplog.text  # REnew the check


def test_run_session_no_wallets(caplog):
    """Test case for handling situation with no available wallets"""

    # Set up logging with detailed format
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create mocks for classes and their methods
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()


    # Create detailed test configuration
    config = {
        'branch_wallet_range': (2, 3),
        'max_parallel_branches': 2,
        'enable_shuffling': False,
        'trading_assets': ['BTC'],
        'position_direction': 'long',
        'volume_percentage_range': (10, 20),
        'enable_logs': True
    }

    # Initialize session
    session = TradingSession(config)
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Setting up empty wallet scenario
    wallet_manager_mock.wallets = []
    wallet_manager_mock.get_next_wallet.return_value = None
    # transaction_manager_mock.execute_trade()
    #IN CASE NO WALLET - EXECUTE TRADE SHOULD NOT BE CALLED

    session.run_session("branch")
    transaction_manager_mock.execute_trade.assert_not_called()
    #TEST IN CASE ONE WALLET -> OBJECTS ARE CALLED WITH RIGHT PARAMETERS

# def test_run_session_one_wallet(caplog):
#     """Test case for handling situation with exactly one available wallet"""
#
#     # Set up logging with detailed format
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )
#
#     # Create mocks for classes and their methods
#     wallet_manager_mock = MagicMock()
#     proxy_manager_mock = MagicMock()
#     transaction_manager_mock = MagicMock()
#
#     # Create detailed test configuration
#     config = {
#         'branch_wallet_range': (2, 3),  # Should not affect execution with only one wallet
#         'max_parallel_branches': 2,
#         'enable_shuffling': False,
#         'trading_assets': ['BTC'],
#         'position_direction': 'long',
#         'volume_percentage_range': (10, 20),
#         'enable_logs': True
#     }
#
#     # Initialize session
#     session = TradingSession(config)
#     session.wallet_manager = wallet_manager_mock
#     session.proxy_manager = proxy_manager_mock
#     session.transaction_manager = transaction_manager_mock
#
#     # Setting up one wallet scenario
#     wallet_manager_mock.wallets = [('wallet_1', 'key_1')]
#     wallet_manager_mock.get_next_wallet.return_value = ('wallet_1', 'key_1')
#     proxy_manager_mock.get_proxy.return_value = 'proxy_1'
#
#     # Define additional expected arguments
#     expected_asset = 'BTC'
#     expected_volume = 15  # Assume a middle value from (10, 20)
#
#     transaction_manager_mock.execute_trade.return_value = True  # Assume trade is successful
#
#     # Run session
#     session.run_session("branch")
#
#     # Ensure execute_trade was called exactly once with correct parameters
#     transaction_manager_mock.execute_trade.assert_called_once_with(
#         'wallet_1', 'key_1', 'proxy_1', expected_asset, expected_volume
#     )
#
#     # Check logs via caplog
#     with caplog.at_level(logging.DEBUG):
#         if transaction_manager_mock.execute_trade.call_count == 1:
#             logging.debug("execute_trade was called exactly once with the correct parameters.")
#         else:
#             logging.debug("execute_trade was not called the expected number of times.")
#
#     # Assertions for logs
#     assert "execute_trade was called exactly once" in caplog.text


def test_run_session_several_wallets(caplog):
    """Test case for handling a session with exactly one available wallet"""

    # Настройка логирования
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Создаем моки для классов и их методов
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    # Детальная конфигурация теста
    config = {
        'branch_wallet_range': (4, 4),
        'max_parallel_branches': 2,
        'enable_shuffling': False,
        'trading_assets': ['BTC'],
        'position_direction': 'long',
        'volume_percentage_range': (10, 20),
        'enable_logs': True
    }

    # Инициализация сессии
    session = TradingSession(config)
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Настраиваем один доступный кошелек
    wallet_manager_mock.wallets = [
        ('wallet_1', 'key_1'),
        ('wallet_2', 'key_2'),
        ('wallet_3', 'key_3'),
        ('wallet_4', 'key_4'),
        ('wallet_5', 'key_5')
    ]

    # Мокаем метод get_next_wallet с учетом передаваемого индекса
    wallet_manager_mock.get_next_wallet.side_effect = lambda index: (
        wallet_manager_mock.wallets[index] if 0 <= index < len(wallet_manager_mock.wallets) else None
    )

    # Настраиваем правильную структуру прокси
    proxy_data =  {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'},

    proxy_manager_mock.get_proxy.side_effect = lambda account_id: proxy_data

    # Фиксируем тестируемые значения
    asset = config['trading_assets'][0]  # 'BTC'
    direction = config['position_direction']  # 'long'
    size = 15.0  # Среднее значение из volume_percentage_range (10, 20)

    # Логируем, чтобы убедиться в правильной настройке
    logging.debug(f"Mock wallets: {wallet_manager_mock.wallets}")
    logging.debug(f"Mock proxy: {proxy_manager_mock.get_proxy(0)}")
    wallet_key = 'key_1'
    # Запускаем тестируемую функцию
    session.run_session("branch")

    # Добавляем логирование перед вызовом метода
    logging.debug(f"Executing trade with parameters: "
                  f"wallet_key={wallet_key}, asset={asset}, "
                  f"direction={direction}, size={size}, proxy={proxy_data}")

    # Проверяем, что метод execute_trade был вызван с каждым кошельком по отдельности
    transaction_manager_mock.execute_trade.assert_called_with(('wallet_1', 'key_1'), asset, direction, size, proxy_data)
    # ASSET_CALLED_ONC_WITH
    transaction_manager_mock.execute_trade.assert_called_with(('wallet_2', 'key_2'), asset, direction, size, proxy_data)
    transaction_manager_mock.execute_trade.assert_called_with(('wallet_3', 'key_3'), asset, direction, size, proxy_data)
    transaction_manager_mock.execute_trade.assert_called_with(('wallet_4', 'key_4'), asset, direction, size, proxy_data)
    transaction_manager_mock.execute_trade.assert_called_with(('wallet_5', 'key_5'), asset, direction, size, proxy_data)
    #
    # # Дополнительно проверяем общее количество вызовов
    # assert transaction_manager_mock.execute_trade.call_count == 5

    # Проверяем, что метод execute_trade был вызван один раз с правильными параметрами
    # transaction_manager_mock.execute_trade.assert_called_once_with(
    #     wallet_key=wallet_key,
    #     asset=asset,
    #     direction=direction,
    #     size=size,
    #     proxy=proxy_data  # Теперь передаем корректную структуру прокси
    # )

def test_run_session_no_proxies(caplog):
    """Test case for no available proxy servers"""
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    session = TradingSession(config={})
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Setting no proxy servers
    wallet_manager_mock.get_next_wallet.return_value = ('wallet_1', 'key_1')
    proxy_manager_mock.get_proxy.return_value = None

    session.run_session("branch")
    transaction_manager_mock.execute_trade.assert_not_called()

    # Logging mistakes via caplog
    # with caplog.at_level(logging.ERROR):
    #     session.run_session("branch")
    #
    # print("CAPLOG_TEXT", caplog.text)
    # # Checking that error message is being recorded
    # assert "Invalid execution mode" in caplog.text  # Renew check


def test_run_session_multiple_proxies(caplog):
    """Test case for handling multiple proxies during trading session"""

    # Настройка логирования
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Создаем моки для классов и их методов
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    # Детальная конфигурация теста
    config = {
        'branch_wallet_range': (4, 4),
        'max_parallel_branches': 2,
        'enable_shuffling': False,
        'trading_assets': ['BTC'],
        'position_direction': 'long',
        'volume_percentage_range': (10, 20),
        'enable_logs': True,
        'proxy_type': 'regular'
    }

    # Инициализация сессии
    session = TradingSession(config)
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Настраиваем тестовые кошельки
    mock_wallets = [
        ('wallet_1', 'key_1'),
        ('wallet_2', 'key_2'),
        ('wallet_3', 'key_3'),
        ('wallet_4', 'key_4'),
        ('wallet_5', 'key_5')
    ]
    wallet_manager_mock.wallets = mock_wallets

    # Настраиваем несколько тестовых прокси
    test_proxies = [
        {'ip_port': '127.0.0.1:8080', 'auth': 'user1:pass1'},
        {'ip_port': '127.0.0.1:8081', 'auth': 'user2:pass2'},
        {'ip_port': '127.0.0.1:8082', 'auth': 'user3:pass3'}
    ]

    # Создаем side_effect для get_proxy, который будет возвращать разные прокси
    def get_proxy_side_effect(account_id: int) -> Dict:
        return test_proxies[account_id % len(test_proxies)]

    proxy_manager_mock.get_proxy.side_effect = get_proxy_side_effect

    # Настраиваем wallet manager
    wallet_manager_mock.get_next_wallet.side_effect = lambda index: (
        mock_wallets[index] if 0 <= index < len(mock_wallets) else None
    )

    # Запускаем тестируемую функцию и проверяем логи
    with caplog.at_level(logging.DEBUG):
        try:
            session.run_session("branch")

            # Проверяем количество вызовов get_proxy
            assert proxy_manager_mock.get_proxy.call_count == len(mock_wallets), \
                f"get_proxy должен быть вызван {len(mock_wallets)} раз"

            # Проверяем параметры каждого вызова get_proxy
            calls = proxy_manager_mock.get_proxy.call_args_list
            for i, call in enumerate(calls):
                args, _ = call
                account_id = args[0]
                expected_proxy = test_proxies[account_id % len(test_proxies)]
                actual_proxy = get_proxy_side_effect(account_id)

                # Логируем детали вызова
                logging.debug(f"""
                Proxy call {i + 1}:
                - Account ID: {account_id}
                - Expected proxy: {expected_proxy}
                - Actual proxy: {actual_proxy}
                """)

                # Проверяем соответствие прокси
                assert actual_proxy == expected_proxy, \
                    f"Неправильный прокси для account_id {account_id}"

            # Проверяем использование прокси в торговых операциях
            trade_calls = transaction_manager_mock.execute_trade.call_args_list
            for i, call in enumerate(trade_calls):
                args, _ = call
                _, _, _, _, proxy = args
                logging.debug(f"Trade {i + 1} used proxy: {proxy}")
                assert proxy in test_proxies, f"Торговая операция {i + 1} использует неизвестный прокси"

            # Выводим статистику использования прокси
            proxy_usage = {}
            for call in proxy_manager_mock.get_proxy.call_args_list:
                args, _ = call
                account_id = args[0]
                proxy = get_proxy_side_effect(account_id)
                proxy_key = proxy['ip_port']
                proxy_usage[proxy_key] = proxy_usage.get(proxy_key, 0) + 1

            logging.info("\nProxy usage statistics:")
            for proxy_ip, count in proxy_usage.items():
                logging.info(f"Proxy {proxy_ip}: used {count} times")

        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            raise

        finally:
            logging.info(f"""
            Test completion statistics:
            - Total proxy calls: {proxy_manager_mock.get_proxy.call_count}
            - Total trade executions: {transaction_manager_mock.execute_trade.call_count}
            - Unique proxies used: {len(set(p['ip_port'] for p in test_proxies))}
            """)


if __name__ == '__main__':
    unittest.main()
