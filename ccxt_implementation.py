import ccxt

def fetch_order_book(exchange, symbol, limit=10):
    try:
        # Create a Kraken exchange object
        kraken = ccxt.kraken()

        # Fetch the order book
        order_book = kraken.fetch_order_book(symbol, limit=limit)

        return order_book

    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Set the symbol and limit
symbol = 'XXBTZEUR'
limit = 10
exchange = 'coinbase'

# Fetch the order book
order_book = fetch_order_book(exchange, symbol, limit)

# Print the order book
print(f"{exchange} {symbol} Order Book:")
print(f"Bids:\n{order_book['bids']}")
print(f"Asks:\n{order_book['asks']}")
