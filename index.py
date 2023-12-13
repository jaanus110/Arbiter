"""
index.py

This is the main file for bot that finds crypto arbitrage opportunities between exchanges.
"""
import asyncio
import pandas as pd

from data_fetch import get_orderbooks
from orderbook_preparation import combine_and_sort_order_book, calculate_fees, clean_order_book, update_filled_orders
from matching_engine import match_orders
from save_results import update_and_save_filled_orders, create_and_save_daily_profit_entry
from user_input import get_user_input
from read_starting_info import initialize_matched_orders_today, initialize_trades_today


async def main():
    # Initialize variables and read previous data into memory
    total_profit = 0
    coinmetro_fee, kraken_fee, sleep_duration = get_user_input()
    matched_orders_today = initialize_matched_orders_today()
    trades_today = initialize_trades_today()

    # Loop searching for arbitrage opportunities until termination by user.
    while True:
        # Fetch the bids and asks from Coinmetro and Kraken
        coinmetro_orders, kraken_orders = await get_orderbooks()

        #Check if orders are not None, i.e. there wasn't any error
        if coinmetro_orders is None or kraken_orders is None:
            print("\nError fetching order books. Terminating.")
            break

        # Combine and sort orderbooks
        book = combine_and_sort_order_book(coinmetro_orders, kraken_orders)

        # Calculate fees
        book = calculate_fees(book, coinmetro_fee, kraken_fee)

        # Clean orderbook from orders that cannot be matched and if applicable, display error that no arbitrage opportunities found.
        book = clean_order_book(book)

        if not book.empty:
            # Process the existing 'book' data
            book = update_filled_orders(book, matched_orders_today)

            #Save current orderbook for error-checking
            #timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H-%M-%S")
            #book.to_excel(timestamp + ' orderbook.xlsx', index=False)
            
            # Match orders
            matched_trades, matching_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity = match_orders(book)

            # Update and save filled orders file
            matched_trades = pd.DataFrame(matched_trades)
            matched_orders_today = update_and_save_filled_orders(matched_orders_today, matched_trades)
            
            # Save daily profit data to excel file and update the variable in memory for later comparison
            trades_today = create_and_save_daily_profit_entry(trades_today, matching_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity)

            # Print the matched trades, profit for these matches and total profit so far
            print("Matched Trades:")
            print(matched_trades)
            print(f"Profit for these trades at {pd.Timestamp.now().strftime('%Y-%m-%d %H-%M-%S')}: {matching_profit} EUR")
            total_profit += matching_profit
            print(f"Total profit so far while running this instance of the script: {total_profit}\n")

        # Wait for x seconds before restarting the loop
        try:
            await asyncio.sleep(sleep_duration)
        except asyncio.CancelledError:
            # Handle cancellation (e.g., user interrupt)
            print("\nScript terminated by user. (Error code 1)")
            break  # Exit the loop if cancelled

if __name__ == "__main__":
    asyncio.run(main())