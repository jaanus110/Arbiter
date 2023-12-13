"""
data_fetch.py

This module contains functions for fetching order book data from Coinmetro and Kraken.
"""

import asyncio
import requests
import ccxt
import pandas as pd


def transform_coinmetro_order_book(coinmetro_order_book):
    """
    Transforms the raw Coinmetro order book data.

    Parameters:
    - coinmetro_order_book (dict): Raw order book data from the Coinmetro exchange.

    Returns:
    - list: Transformed order book containing tuples (price, quantity, ask/bid, exchange).
    """
    coinmetro_bids = list(coinmetro_order_book.get('bid', {}).items())
    coinmetro_bids = [(float(price), float(quantity), 'Bid') for price, quantity in coinmetro_bids]
    coinmetro_asks = list(coinmetro_order_book.get('ask', {}).items())
    coinmetro_asks = [(float(price), float(quantity), 'Ask') for price, quantity in coinmetro_asks]
    coinmetro_orders = coinmetro_bids + coinmetro_asks
    coinmetro_orders = [(price, quantity, ask_bid, 'coinmetro') for price, quantity, ask_bid in coinmetro_orders]
    return coinmetro_orders


def transform_ccxt_exchange_order_book(exchange_order_book, exchange):
    """
    Transforms the raw order book data from a CCXT exchange.

    Parameters:
    - exchange_order_book (dict): Raw order book data from the CCXT exchange.
    - exchange (str): Name of the exchange.

    Returns:
    - list: Transformed order book containing tuples (price, quantity, ask/bid, exchange).
    """
    exchange_bids = exchange_order_book.get('bids', [])
    exchange_bids = [(price, quantity, 'Bid') for price, quantity, _ in exchange_bids]
    exchange_asks = exchange_order_book.get('asks', [])
    exchange_asks = [(price, quantity, 'Ask') for price, quantity, _ in exchange_asks]
    exchange_orders = exchange_bids + exchange_asks
    exchange_orders = [(price, quantity, ask_bid, exchange) for price, quantity, ask_bid in exchange_orders]
    return exchange_orders

async def fetch_coinmetro_order_book():
    """
    Fetches BTCEUR order book data from Coinmetro.

    Parameters:
    - coinmetro_url (str): The API endpoint for the Coinmetro order book.

    Returns:
    - tuple: A tuple containing bid and ask information as lists.
    """
    try:
        # Coinmetro API endpoint for BTCEUR order book
        coinmetro_url = 'https://api.coinmetro.com/exchange/book/BTCEUR'

        # print(f"Started to fetch Coinmetro orderbook at {pd.Timestamp.now()}")

        # Fetch Coinmetro order book data
        # print(f'Started to fetch Coinmetro orderbook at: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}')
        coinmetro_response = requests.get(coinmetro_url)
        # print(f'Received Coinmetro orderbook at: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}')

        # Check if the Coinmetro request was successful (HTTP status code 200)
        if coinmetro_response.status_code == 200:
            coinmetro_order_book_data = coinmetro_response.json()

            if 'book' in coinmetro_order_book_data:
                return transform_coinmetro_order_book(coinmetro_order_book_data['book'])

            else:
                timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Error: 'book' key not found in Coinmetro order book data. ", timestamp)
        else:
            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Error fetching Coinmetro order book data. Status code: {coinmetro_response.status_code} ", timestamp)

    except asyncio.CancelledError:
        print(f"Coinmetro orderbook fetching terminated by user.")
        return None, None


async def fetch_ccxt_exchange_order_book(exchange_name, symbol, limit=10):
    """
    Fetches the order book from the specified exchange and transforms it.

    Parameters:
    - exchange_name (str): Name of the exchange (e.g., 'kraken', 'binance').
    - symbol (str): Trading symbol for the order book (e.g., 'BTC/USD').
    - limit (int): Number of order book levels to retrieve (default is 10).

    Returns:
    - list: Transformed order book containing tuples (price, quantity, ask/bid, exchange).
    """
    try:
         # Get the CCXT exchange class dynamically
        exchange_class = getattr(ccxt, exchange_name.lower())  # Assuming exchange names are lowercase

        # Create an instance of the exchange class
        exchange = exchange_class()

        # Use asyncio.to_thread to run synchronous code (requests) in a separate thread
        # print(f'Started to fetch {exchange_name} orderbook at: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}')
        order_book = await asyncio.to_thread(exchange.fetch_order_book, symbol, limit)
        # print(f'Received {exchange_name} orderbook at: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}')
        #transform book
        return transform_ccxt_exchange_order_book(order_book, exchange_name)

    except ccxt.NetworkError as e:
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")     
        print(f"Network error: {e}, {timestamp}")
    except ccxt.ExchangeError as e:
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")     
        print(f"Exchange error: {e}, {timestamp}")
    except Exception as e:
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")     
        print(f"An error occurred: {e}, {timestamp}")
    except asyncio.CancelledError:
        print(f"{exchange} Orderbook fetching terminated by user.")
        return None, None


async def get_orderbooks():
    """
    Fetches order book data concurrently from Coinmetro and Kraken.

    Returns:
    - list: A list containing bid and ask information for Coinmetro and Kraken.
    """
    try:
        # Use asyncio.create_task to start both tasks concurrently
        kraken_orders_task = asyncio.create_task(fetch_ccxt_exchange_order_book("kraken", "XXBTZEUR"))
        coinmetro_orders_task = asyncio.create_task(fetch_coinmetro_order_book())

        # Use asyncio.gather to wait for both tasks to complete
        kraken_orders, coinmetro_orders = await asyncio.gather(kraken_orders_task, coinmetro_orders_task)
        return coinmetro_orders, kraken_orders
        
    except asyncio.CancelledError:
        print("Orderbook fetching terminated by user.")
        return None, None