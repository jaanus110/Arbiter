import pandas as pd
import os
import ccxt


def initialize_matched_orders_today(temp_directory=""):
    # Define expected_columns outside the try-except block
    expected_columns = ['Timestamp', 'Price', 'Quantity', 'Ask/Bid', 'Exchange', 'Fee', 'Net Price', 'Matched Quantity', 'Remaining Quantity']
    
    try:
        matched_orders_filename = os.path.join(temp_directory, pd.Timestamp.now().strftime("%Y-%m-%d") + ' matched_orders.xlsx')
        matched_orders_today = pd.read_excel(matched_orders_filename)
        # If the DataFrame is empty, enforce the expected columns
        if matched_orders_today.empty:
            matched_orders_today = pd.DataFrame(columns=expected_columns)
        # Ensure that the columns are as expected
        if not set(expected_columns).issubset(matched_orders_today.columns):
            raise ValueError(f"Columns mismatch. Expected: {expected_columns}, Actual: {matched_orders_today.columns}")
    except FileNotFoundError:
        matched_orders_today = pd.DataFrame(columns=expected_columns)
    return matched_orders_today


def initialize_trades_today(temp_directory=""):
    # Initialize trades_today. It is used to calculate the capital allocation requirements, daily profits, and profitability.
    try:
        trades_filename = os.path.join(temp_directory, pd.Timestamp.now().strftime("%Y-%m-%d") + ' trades.xlsx')
        trades_today = pd.read_excel(trades_filename)
    except FileNotFoundError:
        # Create an empty DataFrame if the file does not exist
        trades_today = pd.DataFrame(columns=['Timestamp', 'Profit', 'Kraken BTC', 'Kraken EUR', 'Coinmetro BTC', 'Coinmetro EUR'])
    return trades_today


def fetch_kraken_taker_fee():
    try:
        # Create an instance of the Kraken exchange class
        kraken = ccxt.kraken()

        # Fetch exchange information, including trading fees
        exchange_info = kraken.fetch_markets()

        # Find the trading pair you are interested in (e.g., 'BTC/USD')
        trading_pair = 'BTC/EUR'
        market = next(m for m in exchange_info if m['symbol'] == trading_pair)

        # Extract taker fee from the market information
        taker_fee = market['taker']

        return float(taker_fee) * 100  # Convert to percentage

    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
