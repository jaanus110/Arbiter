"""
matching_engine.py

This module contains the code to match orders to find arbitrage opportunities.
"""
import pandas as pd

def match_orders(book):
    """
    Matches bid and ask orders to find arbitrage opportunities.

    Parameters:
    - book (DataFrame): The combined and sorted order book containing bid and ask information.

    Returns:
    - tuple: A tuple containing a list of matched trades, total matching profit, and quantities for Kraken and Coinmetro (BTC and EUR).
    """
    matched_trades = []
    matching_profit = 0
    kraken_btc_quantity = 0
    kraken_eur_quantity = 0
    coinmetro_btc_quantity = 0
    coinmetro_eur_quantity = 0

    #print('BOOK:\n')
    #print(book)
    #print(f"Book datatype in the beginning of match_orders: {type(book)}")

    # Iterate over the ask rows of the book DataFrame. Start with ask rows with lowest net price.
    #print("Starting with ask_row [bid_row] iterations")
    for _, ask_row in book[book['Ask/Bid'] == 'Ask'].iterrows():
        #print(f"ask_row no {_}")
        # Filter bid orders with a higher net price and reverse the order. This starts iteration of bid rows with highest net price.
        bid = book[(book['Ask/Bid'] == 'Bid') & (book['Net Price'] > ask_row['Net Price'])][::-1]
        for _, bid_row in bid.iterrows():
            #print(f"bid_row no {_}")
            # Determine the maximum quantity that can be matched
            max_quantity = min(ask_row['Remaining Quantity'], bid_row['Remaining Quantity'])
            #print(f"Matching trades. Ask Price: {ask_row['Price']}, Ask Quantity: {ask_row['Remaining Quantity']}, Bid Price: {bid_row['Price']}, Bid Quantity: {bid_row['Remaining Quantity']}, Matched Quantity: {max_quantity}, Ask Exchange: {ask_row['Exchange']}, Bid Exchange: {bid_row['Exchange']}")
            
            # Update trade information for profit calculation and saving.
            if max_quantity > 0:
                trade_profit = max_quantity * (bid_row['Net Price'] - ask_row['Net Price'])
                matching_profit += trade_profit

                # Update quantities based on the matched trades
                if bid_row['Exchange'] == 'Kraken':
                    kraken_btc_quantity -= max_quantity
                    kraken_eur_quantity += bid_row['Net Price'] * max_quantity
                elif bid_row['Exchange'] == 'Coinmetro':
                    coinmetro_eur_quantity += bid_row['Net Price'] * max_quantity
                    coinmetro_btc_quantity -= max_quantity

                if ask_row['Exchange'] == 'Kraken':
                    kraken_eur_quantity -= ask_row['Net Price'] * max_quantity
                    kraken_btc_quantity += max_quantity
                elif ask_row['Exchange'] == 'Coinmetro':
                    coinmetro_eur_quantity -= ask_row['Net Price'] * max_quantity
                    coinmetro_btc_quantity += max_quantity

                # Update the bid and ask quantity by subtracting max_quantity
                book.at[bid_row.name, 'Remaining Quantity'] -= max_quantity
                bid_row['Remaining Quantity'] -= max_quantity                
                book.at[ask_row.name, 'Remaining Quantity'] -= max_quantity
                ask_row['Remaining Quantity'] -= max_quantity                

                current_timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

                # Add executed trades to mached_trades
                ask_trade_data = {
                    'Timestamp': current_timestamp,
                    'Price': ask_row['Price'],
                    'Quantity': ask_row['Quantity'],
                    'Ask/Bid': ask_row['Ask/Bid'],
                    'Exchange': ask_row['Exchange'],
                    'Fee': ask_row['Fee'],
                    'Net Price': ask_row['Net Price'],
                    'Matched Quantity': max_quantity,
                    'Remaining Quantity': ask_row['Remaining Quantity']
                }

                bid_trade_data = {
                    'Timestamp': current_timestamp,
                    'Price': bid_row['Price'],
                    'Quantity': bid_row['Quantity'],
                    'Ask/Bid': bid_row['Ask/Bid'],
                    'Exchange': bid_row['Exchange'],
                    'Fee': bid_row['Fee'],
                    'Net Price': bid_row['Net Price'],
                    'Matched Quantity': max_quantity,
                    'Remaining Quantity': bid_row['Remaining Quantity']
                }

                matched_trades.append(ask_trade_data)
                matched_trades.append(bid_trade_data)

                if ask_row['Remaining Quantity'] == 0 or bid_row['Remaining Quantity'] == 0:
                    break

        if ask_row['Remaining Quantity'] == 0:
            break
        
    # Switch the order of iteration
    #print("Switching to bid_row [ask_row] iterations")
    for _, bid_row in book[book['Ask/Bid'] == 'Bid'].iterrows():
        #print(f"bid_row no {_}")
        # Filter ask orders with a lower net price. This starts iteration of ask rows with lowest net price.
        ask = book[(book['Ask/Bid'] == 'Ask') & (book['Net Price'] < bid_row['Net Price'])]
        
        for _, ask_row in ask.iterrows():
            #print(f"ask_row no {_}")
            #print(f"Matching trades. Ask Price: {ask_row['Price']}, Ask Quantity: {ask_row['Remaining Quantity']}, Bid Price: {bid_row['Price']}, Bid Quantity: {bid_row['Remaining Quantity']}, Matched Quantity: {max_quantity}, Ask Exchange: {ask_row['Exchange']}, Bid Exchange: {bid_row['Exchange']}")
            # Continue with the rest of the logic for matching trades between bid and ask rows
            # Determine the maximum quantity that can be matched
            max_quantity = min(ask_row['Remaining Quantity'], bid_row['Remaining Quantity'])
            #print(f"Matching trades. Ask Price: {ask_row['Price']}, Ask Quantity: {ask_row['Remaining Quantity']}, Bid Price: {bid_row['Price']}, Bid Quantity: {bid_row['Remaining Quantity']}, Matched Quantity: {max_quantity}, Ask Exchange: {ask_row['Exchange']}, Bid Exchange: {bid_row['Exchange']}")
            
            # Update trade information for profit calculation and saving.
            if max_quantity > 0:
                trade_profit = max_quantity * (bid_row['Net Price'] - ask_row['Net Price'])
                matching_profit += trade_profit

                # Update quantities based on the matched trades
                if bid_row['Exchange'] == 'Kraken':
                    kraken_btc_quantity -= max_quantity
                    kraken_eur_quantity += bid_row['Net Price'] * max_quantity
                elif bid_row['Exchange'] == 'Coinmetro':
                    coinmetro_eur_quantity += bid_row['Net Price'] * max_quantity
                    coinmetro_btc_quantity -= max_quantity

                if ask_row['Exchange'] == 'Kraken':
                    kraken_eur_quantity -= ask_row['Net Price'] * max_quantity
                    kraken_btc_quantity += max_quantity
                elif ask_row['Exchange'] == 'Coinmetro':
                    coinmetro_eur_quantity -= ask_row['Net Price'] * max_quantity
                    coinmetro_btc_quantity += max_quantity

                # Update the bid and ask quantity by subtracting max_quantity
                book.at[bid_row.name, 'Remaining Quantity'] -= max_quantity
                bid_row['Remaining Quantity'] -= max_quantity                
                book.at[ask_row.name, 'Remaining Quantity'] -= max_quantity
                ask_row['Remaining Quantity'] -= max_quantity                

                current_timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

                # Add executed trades to matched_trades
                ask_trade_data = {
                    'Timestamp': current_timestamp,
                    'Price': ask_row['Price'],
                    'Quantity': ask_row['Quantity'],
                    'Ask/Bid': ask_row['Ask/Bid'],
                    'Exchange': ask_row['Exchange'],
                    'Fee': ask_row['Fee'],
                    'Net Price': ask_row['Net Price'],
                    'Matched Quantity': max_quantity,
                    'Remaining Quantity': ask_row['Remaining Quantity']
                }

                bid_trade_data = {
                    'Timestamp': current_timestamp,
                    'Price': bid_row['Price'],
                    'Quantity': bid_row['Quantity'],
                    'Ask/Bid': bid_row['Ask/Bid'],
                    'Exchange': bid_row['Exchange'],
                    'Fee': bid_row['Fee'],
                    'Net Price': bid_row['Net Price'],
                    'Matched Quantity': max_quantity,
                    'Remaining Quantity': bid_row['Remaining Quantity']
                }

                matched_trades.append(ask_trade_data)
                matched_trades.append(bid_trade_data)

                if ask_row['Remaining Quantity'] == 0 or bid_row['Remaining Quantity'] == 0:
                    break
        if bid_row['Remaining Quantity'] == 0:
            break

    return matched_trades, matching_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity
