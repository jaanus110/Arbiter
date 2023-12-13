"""
orderbook_preparation.py

This is the file to combine data retrieved from multiple exchanges into a single orderbook and process this orderbook for matching.
"""

import pandas as pd

def combine_and_sort_order_book(coinmetro_orders, kraken_orders):
    """
    Combines and sorts bid and ask data from Coinmetro and Kraken.

    Parameters:
    - coinmetro_orders (list): List of Coinmetro orders.
    - kraken_orders (list): List of Kraken orders.

    Returns:
    - pd.DataFrame: Sorted order book data.
    """
    # Combine bid and ask data from Coinmetro and Kraken
    combined_data = coinmetro_orders + kraken_orders

    # Create DataFrame for sorted order book data
    book = pd.DataFrame(combined_data, columns=['Price', 'Quantity', "Ask/Bid", "Exchange"])

    book = book.sort_values(by='Price')

    # Reset the index after sorting
    book = book.reset_index(drop=True)

    return book


def calculate_fees(book, coinmetro_fee, kraken_fee):
    """
    Adjust prices in the order book DataFrame based on specific rules for each exchange.

    Args:
    - book (pd.DataFrame): DataFrame containing order book data.

    Returns:
    - pd.DataFrame: Updated order book DataFrame with adjusted prices.
    """
    # Calculate fees and net prices
    book['Fee'] = book.apply(lambda row: kraken_fee * row['Price'] if row['Exchange'] == 'Kraken' else coinmetro_fee * row['Price'], axis=1)
    book['Net Price'] = book.apply(lambda row: row['Price'] - row['Fee'] if row['Ask/Bid'] == 'Bid' else row['Price'] + row['Fee'], axis=1)
                    
    # Sort the DataFrame by the 'Net Price' column in ascending order
    book = book.sort_values(by='Net Price')

    # Reset the index after sorting
    book = book.reset_index(drop=True)

    return book


def calculate_spread(book):
    """
    Calculate the price difference and spread percentage between the highest Bid Net Price and lowest Ask Net Price.

    Parameters:
    - book (pd.DataFrame): The order book data containing 'Ask/Bid' and 'Net Price' columns.

    Returns:
    - float: Hihgest bid net price.
    - float: Lowest ask net price.
    - float: The calculated price difference between highest Bid Net Price and lowest Ask Net Price.
    - float: The calculated spread percentage.
    
    Example:
    calculate_spread(book)
    """
    # Find the highest Net Price for a Bid
    highest_bid_net_price = book.loc[book['Ask/Bid'] == 'Bid', 'Net Price'].max()

    # Find the lowest Net Price for an Ask
    lowest_ask_net_price = book.loc[book['Ask/Bid'] == 'Ask', 'Net Price'].min()

    # Calculate the difference between the highest Bid Net Price and lowest Ask Net Price
    price_difference = round (highest_bid_net_price - lowest_ask_net_price, 3)
    spread_percentage = round((price_difference/lowest_ask_net_price) * 100, 4)
    
    return highest_bid_net_price, lowest_ask_net_price, price_difference, spread_percentage


def clean_order_book(book):
    """
    Cleans the order book DataFrame by keeping rows from the first 'Ask' to the last 'Bid'. Removed lines couldn't be matched.

    Parameters:
    - book (pd.DataFrame): The order book data to be filtered.

    Returns:
    - pd.DataFrame: The filtered order book data.
    """
    # Get variables to display in case there is no arbitrage opportunities
    highest_bid_net_price, lowest_ask_net_price, price_difference, spread_percentage = calculate_spread(book)

    # Find the row number of the first Ask
    first_ask_row = book[book['Ask/Bid'] == 'Ask'].index[0]

    # Drop rows before the first Ask
    book = book.iloc[first_ask_row:]
    #print(f"This is book after dropping rows before the first Ask:\n {book}")

    # Reset the index of the DataFrame
    book = book.reset_index(drop=True)

    # Find the row number of the last Bid
    bid_rows = book[book['Ask/Bid'] == 'Bid']

    if bid_rows.empty:
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"No arbitrage opportunities. Highest bid: {highest_bid_net_price}, lowest ask: {lowest_ask_net_price}, spread: {price_difference} EUR/BTC ({spread_percentage} %), {timestamp}")
        return pd.DataFrame()  # Return an empty DataFrame if no arbitrage opportunities

    last_bid_row = bid_rows.index[-1]

    # Drop rows after the last Bid
    book = book.iloc[:last_bid_row + 1]

    # Reset the index of the DataFrame
    book = book.reset_index(drop=True)

    return book


def update_filled_orders(book, matched_orders_today):
    """
    Processes the existing 'book' data from a file and removes matching rows from the order book.

    Parameters:
    - book (pd.DataFrame): The order book data to be processed.
    - matched_orders_today (pd.DataFrame): The DataFrame containing matched orders for the day.

    Returns:
    - pd.DataFrame: The processed order book data.
    """
    # Step 1: Create a new column "Remaining Quantity" in book
    book['Remaining Quantity'] = book['Quantity'].copy()

    # Step 2: Merge book and matched_orders_today based on specified columns
    merged_df = pd.merge(book, matched_orders_today, on=["Price", "Quantity", "Ask/Bid", "Exchange"], how="inner", suffixes=('', '_matched'))

    # Step 3: Update "Remaining Quantity" in book with the minimum value from matched_orders_today
    for index, row in merged_df.iterrows():
        matching_rows = (book["Price"] == row["Price"]) & (book["Quantity"] == row["Quantity"]) & (book["Ask/Bid"] == row["Ask/Bid"]) & (book["Exchange"] == row["Exchange"])

        # If there is a match in the book, update the "Remaining Quantity"
        if matching_rows.any():
            # Start with the current value of "Remaining Quantity"
            min_remaining_quantity = row["Remaining Quantity_matched"]

            # Update "Remaining Quantity" in the book DataFrame with the minimum value
            if min_remaining_quantity > 0:
                # Use iloc to access the DataFrame by integer location
                book.loc[matching_rows, 'Remaining Quantity'] = book.loc[matching_rows, 'Remaining Quantity'].apply(lambda x: min(min_remaining_quantity, x))
    # Step 4: Drop unnecessary columns from the merged DataFrame
    merged_df = merged_df.drop(columns=['Remaining Quantity_matched'])

    # Optionally, drop duplicates from the book DataFrame
    book = book.drop_duplicates()

    return book
