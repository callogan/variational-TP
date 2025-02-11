from trading_ui_automation import TradingPlatformUI
import logging

def test_ui_automation():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Initialize UI automation
    ui = TradingPlatformUI(headless=False)  # Set to False to see browser actions
    
    try:
        # Start session
        ui.start_session("Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        # Test each UI function
        ui.add_to_waitlist("test@example.com")
        ui.connect_wallet("0x1234...")
        ui.create_portfolio()
        ui.make_deposit()
        ui.select_asset("BTC")
        ui.execute_trade("long", 1000)
        ui.close_position()
        
    except Exception as e:
        logging.error(f"UI automation error: {str(e)}")
    
    finally:
        ui.close_session()

if __name__ == "__main__":
    test_ui_automation() 