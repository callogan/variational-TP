import logging
import unittest
from crypto_trading_bot import TradingSession
from unittest.mock import patch, MagicMock


@patch('crypto_trading_bot.time.sleep', return_value=None)  # Suppress delay in tests
def test_run_session_success(caplog):
    """Test successful execution of one trading session iteration"""

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Create mocks for classes and their methods
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    # Create session object
    session = TradingSession(config={})
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Set return values for mocks
    wallet_manager_mock.get_next_wallet.return_value = ('wallet_1', 'key_1')
    proxy_manager_mock.get_next_proxy.return_value = 'proxy_1'
    transaction_manager_mock.execute_transaction.return_value = True

    # Run session
    session.run_session(1)  # One iteration

    # Check logs via caplog
    with caplog.at_level(logging.DEBUG):
        # Log the number of times the get_next_wallet method was called
        if wallet_manager_mock.get_next_wallet.call_count > 0:
            logging.debug(f'get_next_wallet was called {wallet_manager_mock.get_next_wallet.call_count} time(s)')
        else:
            logging.debug('get_next_wallet was not called')

        # Log the number of times the get_next_proxy method was called
        if proxy_manager_mock.get_next_proxy.call_count > 0:
            logging.debug(f'get_next_proxy was called {proxy_manager_mock.get_next_proxy.call_count} time(s)')
        else:
            logging.debug('get_next_proxy was not called')

        # Log the number of times the execute_transaction method was called
        if transaction_manager_mock.execute_transaction.call_count > 0:
            logging.debug(f'execute_transaction was called {transaction_manager_mock.execute_transaction.call_count} time(s)')
        else:
            logging.debug('execute_transaction was not called')

    # Verify that the proxy and transaction methods were called once
    proxy_manager_mock.get_next_proxy.assert_called_once()
    transaction_manager_mock.execute_transaction.assert_called_once_with('wallet_1', 'key_1', 'proxy_1')

    # Check that the logs contain the expected messages
    assert 'get_next_wallet was called' in caplog.text
    assert 'get_next_proxy was called' in caplog.text
    assert 'execute_transaction was called' in caplog.text


def test_run_session_no_wallets(caplog):
    """Test case for no available wallets"""
    wallet_manager_mock = MagicMock()
    proxy_manager_mock = MagicMock()
    transaction_manager_mock = MagicMock()

    session = TradingSession(config={})
    session.wallet_manager = wallet_manager_mock
    session.proxy_manager = proxy_manager_mock
    session.transaction_manager = transaction_manager_mock

    # Setting no wallets
    wallet_manager_mock.get_next_wallet.return_value = None

    # Logging mistakes via caplog
    with caplog.at_level(logging.ERROR):
        session.run_session(1)

    # Checking that error message is being recorded
    assert "Invalid execution mode" in caplog.text  # REnew the check


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
    proxy_manager_mock.get_next_proxy.return_value = None

    # Logging mistakes via caplog
    with caplog.at_level(logging.ERROR):
        session.run_session(1)

    # Checking that error message is being recorded
    assert "Invalid execution mode" in caplog.text  # Renew check


if __name__ == '__main__':
    unittest.main()
