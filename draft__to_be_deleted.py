import ccxt

def fetch_kraken_taker_fee():
    try:
        # Create an instance of the Kraken exchange class
        kraken = ccxt.kraken()

        # Fetch exchange information, including trading fees
        exchange_info = kraken.fetch_markets()

        # Find the trading pair you are interested in (e.g., 'BTC/USD')
        trading_pair = 'BTC/USD'
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

# Fetch Kraken taker fee
kraken_taker_fee = fetch_kraken_taker_fee()

if kraken_taker_fee is not None:
    print(f"Kraken taker fee: {kraken_taker_fee:.4f}%")
