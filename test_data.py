"""Test data for crypto trading scenarios"""

TEST_WALLETS = [
    {
        "private_key": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "address": "0x1234567890123456789012345678901234567890"
    },
    {
        "private_key": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "address": "0x2345678901234567890123456789012345678901"
    },
    {
        "private_key": "0x2234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "address": "0x3456789012345678901234567890123456789012"
    }
]

TEST_PROXIES = [
    "192.168.1.1:8080@user1:pass1",
    "192.168.1.2:8080@user2:pass2|http://refresh.link/proxy1",
    "192.168.1.3:8080@user3:pass3"
]

TEST_CONFIGS = {
    "parallel_trading": {
        "web3_provider": "https://sepolia-rollup.arbitrum.io/rpc",
        "keys_file": "test_wallet_keys.txt",
        "proxy_file": "test_proxies.txt",
        "proxy_type": "regular",
        "enable_logs": True,
        "enable_shuffling": True,
        "thread_count": 3,
        "launch_delay": (1, 5),  # Shorter delays for testing
        "trading_assets": ["BTC", "ETH", "SOL"],
        "position_direction": "random",
        "volume_percentage_range": (10, 50)
    },
    "branch_trading": {
        "web3_provider": "https://sepolia-rollup.arbitrum.io/rpc",
        "keys_file": "test_wallet_keys.txt",
        "proxy_file": "test_proxies.txt",
        "proxy_type": "mobile",
        "enable_logs": True,
        "enable_shuffling": True,
        "branch_wallet_range": (2, 3),
        "max_parallel_branches": 2,
        "trading_assets": ["BTC", "ETH"],
        "position_direction": "random",
        "volume_percentage_range": (10, 50)
    }
}

TEST_TRADE_SCENARIOS = [
    {
        "name": "basic_long_trade",
        "wallet_index": 0,
        "asset": "BTC",
        "direction": "long",
        "size": 1000,
        "expected_result": "success"
    },
    {
        "name": "basic_short_trade",
        "wallet_index": 1,
        "asset": "ETH",
        "direction": "short",
        "size": 2000,
        "expected_result": "success"
    },
    {
        "name": "insufficient_balance",
        "wallet_index": 2,
        "asset": "SOL",
        "direction": "long",
        "size": 1000000,  # Deliberately large amount
        "expected_result": "failed"
    }
] 