"""
save_results.py

This is the file to save arbitrage results for later.
"""
import pandas as pd
import os

from pathlib import Path

def update_and_save_filled_orders(matched_orders_today, matched_trades, path=""):
    """
    Update the daily filled orders with matched trades and save to an Excel file.

    Parameters:
    - matched_orders_today (pd.DataFrame): The existing daily filled orders DataFrame.
    - matched_trades (list): List containing matched trades data.

    Returns:
    - pd.DataFrame: The updated daily filled orders DataFrame.
    """
    try:
        if not isinstance(matched_orders_today, pd.DataFrame):
            raise ValueError(f"Parameter 'matched_orders_today' must be a DataFrame. However, it is {type(matched_orders_today)}")
        # Check if matched_trades is a list, convert it to a DataFrame if necessary
        if isinstance(matched_trades, list):
            matched_trades = pd.DataFrame(matched_trades)
        # Concatenate the existing data with the matched trades DataFrametched_trades.columns)
        file_path = Path(path) / (pd.Timestamp.now().strftime("%Y-%m-%d") + ' matched_orders.xlsx')
        if not matched_orders_today.empty and not matched_trades.empty:
            matched_orders_today = pd.concat([matched_orders_today, matched_trades], ignore_index=True, sort=False)
            matched_orders_today.to_excel(file_path, index=False, float_format='%.16f')
        elif not matched_trades.empty: 
            matched_orders_today = matched_trades
            matched_orders_today.to_excel(file_path, index=False, float_format='%.16f')
        else:
            print("No matched trades to update.")
    except Exception as e:
        print(f"Error updating and saving filled orders: {str(e)}")
    return matched_orders_today


def create_and_save_daily_profit_entry(trades_today, total_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity, path=""):
    """
    Create a new entry for daily profit, concatenate it with existing daily trades, and save to an Excel file.

    Parameters:
    - trades_today (pd.DataFrame): The existing daily trades DataFrame.
    - total_profit (float): The total profit for the day.
    - kraken_btc_quantity (float): Quantity of BTC traded on Kraken.
    - kraken_eur_quantity (float): Quantity of EUR traded on Kraken.
    - coinmetro_btc_quantity (float): Quantity of BTC traded on Coinmetro.
    - coinmetro_eur_quantity (float): Quantity of EUR traded on Coinmetro.

    Returns:
    - pd.DataFrame: The updated daily trades DataFrame.
    """
    # Create a new entry for daily profit
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a new DataFrame for the daily profit entry
    new_entry = pd.DataFrame([[timestamp, total_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity]],
                             columns=['Timestamp', 'Profit', 'Kraken BTC', 'Kraken EUR', 'Coinmetro BTC', 'Coinmetro EUR'])

    # print(f"new entry into trades and profits:\n{new_entry}")
    # Concatenate the new entry with the existing trades_today DataFrame
    if not trades_today.empty and not new_entry.empty:
        trades_today = pd.concat([trades_today, new_entry], ignore_index=True, sort=False)
    else:
        # Handle the case when one or both DataFrames are empty
        trades_today = new_entry

    # Save the daily profit data to an Excel file
    file_path = Path(path) / (pd.Timestamp.now().strftime("%Y-%m-%d") + ' trades.xlsx')
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        trades_today.to_excel(writer, index=False)
    
    return trades_today
