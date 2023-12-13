# test__orderbook_preparation.py

import pytest
import pandas as pd
from orderbook_preparation import combine_and_sort_order_book, calculate_fees, calculate_spread, clean_order_book, update_filled_orders

coinmetro_bids = [
    ('23428.00', 0.30639636),
    ('23434.99', 0.01001201),
    ('23437.12', 5.02312301)
]

coinmetro_asks = [
    ('23437.2', 0.21239833)
]

kraken_bids = [
    ['23423.09000', '1.200', 1702311080],
    ['23424.02000', '0.005', 1702311076],
]

kraken_asks = [
    ['23425.01000', '0.058', 1702311076],
    ['23426.12000', '2.926', 1702310931],
    ['23431.58000', '0.005', 1702310860],
    ['23433.49000', '1.926', 1702310777],
    ['23436.32000', '0.005', 1702310939],
]
coinmetro_fee = 0.1 / 100
kraken_fee = 0.24 / 100
book = pd.DataFrame({'Price': [23423.09, 23424.02, 23425.01, 23426.12, 23428.00, 23431.58, 23433.49, 23434.99, 23436.32, 23437.12, 23437.20],
                    'Quantity': [1.200000, 0.005000, 0.058000, 2.926000, 0.30639636, 0.005000, 1.926000, 0.01001201, 0.005000, 5.02312301, 0.21239833],
                    'Ask/Bid': ['Bid', 'Bid', 'Ask', 'Ask', 'Bid', 'Ask', 'Ask', 'Bid', 'Ask', 'Bid', 'Ask'],
                    'Exchange': ['Kraken', 'Kraken', 'Kraken', 'Kraken', 'Coinmetro', 'Kraken', 'Kraken', 'Coinmetro', 'Kraken', 'Coinmetro', 'Coinmetro']
                })
def test__combine_and_sort_order_book__empty_input():
    result = combine_and_sort_order_book([], [], [], [])
    assert result.empty
    expected_columns = ['Price', 'Quantity', 'Ask/Bid', 'Exchange']
    assert list(result.columns) == expected_columns

def test__combine_and_sort_order_book__one_empty_input():
    book_in_test = pd.DataFrame({
        'Price': [23423.09, 23424.02, 23425.01, 23426.12, 23431.58, 23433.49, 23436.32, 23437.20],
        'Quantity': [1.200000, 0.005000, 0.058000, 2.926000, 0.005000, 1.926000, 0.005000, 0.21239833],
        'Ask/Bid': ['Bid', 'Bid', 'Ask', 'Ask', 'Ask', 'Ask', 'Ask', 'Ask'],
        'Exchange': ['Kraken', 'Kraken', 'Kraken', 'Kraken', 'Kraken', 'Kraken', 'Kraken', 'Coinmetro']
    })
    assert combine_and_sort_order_book([], coinmetro_asks, kraken_bids, kraken_asks).equals(book_in_test)


def test__combine_and_sort_order_book__normal():
    assert combine_and_sort_order_book(coinmetro_bids, coinmetro_asks, kraken_bids, kraken_asks).equals(book)


def test__calculate_fees__no_fees():
    book_with_fees = pd.DataFrame({
        'Price': [23423.09, 23424.02, 23425.01, 23426.12, 23428.00, 23431.58, 23433.49, 23434.99, 23436.32, 23437.12, 23437.20],
        'Quantity': [1.200000, 0.005000, 0.058000, 2.926000, 0.30639636, 0.005000, 1.926000, 0.01001201, 0.005000, 5.02312301, 0.21239833],
        'Ask/Bid': ['Bid', 'Bid', 'Ask', 'Ask', 'Bid', 'Ask', 'Ask', 'Bid', 'Ask', 'Bid', 'Ask'],
        'Exchange': ['Kraken', 'Kraken', 'Kraken', 'Kraken', 'Coinmetro', 'Kraken', 'Kraken', 'Coinmetro', 'Kraken', 'Coinmetro', 'Coinmetro'],
        'Fee': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Net Price': [23423.09, 23424.02, 23425.01, 23426.12, 23428.00, 23431.58, 23433.49, 23434.99, 23436.32, 23437.12, 23437.20]
    })
    assert calculate_fees(book, 0, 0).equals(book_with_fees)


def test__calculate_fees__normal_fees():
    data = {
        'Price': [23423.09, 23424.02, 23428.00, 23434.99, 23437.12, 23437.20, 23425.01, 23426.12, 23431.58, 23433.49, 23436.32],
        'Quantity': [1.200000, 0.005000, 0.306396, 0.010012, 5.023123, 0.212398, 0.058000, 2.926000, 0.005000, 1.926000, 0.005000],
        'Ask/Bid': ['Bid', 'Bid', 'Bid', 'Bid', 'Bid', 'Ask', 'Ask', 'Ask', 'Ask', 'Ask', 'Ask'],
        'Exchange': ['Kraken', 'Kraken', 'Coinmetro', 'Coinmetro', 'Coinmetro', 'Coinmetro', 'Kraken', 'Kraken', 'Kraken', 'Kraken', 'Kraken'],
        'Fee': [56.215416, 56.217648, 23.428000, 23.434990, 23.437120, 23.437200, 56.220024, 56.222688, 56.235792, 56.240376, 56.247168],
        'Net Price': [23366.874584, 23367.802352, 23404.572000, 23411.555010, 23413.682880, 23460.637200, 23481.230024, 23482.342688, 23487.815792, 23489.730376, 23492.567168]
    }

    book_with_fees = round(pd.DataFrame(data), 6)
    test_book = round(calculate_fees(book, coinmetro_fee, kraken_fee), 6)
    assert test_book.equals(book_with_fees)


def test__calculate_spread__normal():
    test_book = calculate_fees (book, coinmetro_fee, kraken_fee)
    highest_bid_net_price, lowest_ask_net_price, price_difference, spread_percentage = calculate_spread(test_book)
    assert highest_bid_net_price == 23413.68288
    assert lowest_ask_net_price == 23460.6372
    assert price_difference == -46.954
    assert spread_percentage == -0.2001


def test__clean_order_book__no_opportunities():
    test_book = calculate_fees(book, coinmetro_fee, kraken_fee)
    test_book = clean_order_book(test_book)
    print(test_book)
    assert test_book.empty


def test__clean_order_book__normal():
    data = {
        "Price": [23425.009999999998, 23426.119999999999, 23428.000000000000, 23431.580000000002,
                23433.490000000002, 23434.990000000002, 23436.320000000000, 23437.119999999999],
        "Quantity": [0.058000000000, 2.926000000000, 0.306396360000, 0.005000000000,
                    1.926000000000, 0.010012010000, 0.005000000000, 5.023123010000],
        "Ask/Bid": ["Ask", "Ask", "Bid", "Ask", "Ask", "Bid", "Ask", "Bid"],
        "Exchange": ["Kraken", "Kraken", "Coinmetro", "Kraken", "Kraken", "Coinmetro", "Kraken", "Coinmetro"],
        "Fee": [0.000000000000, 0.000000000000, 0.000000000000, 0.000000000000,
                0.000000000000, 0.000000000000, 0.000000000000, 0.000000000000],
        "Net Price": [23425.009999999998, 23426.119999999999, 23428.000000000000, 23431.580000000002,
                    23433.490000000002, 23434.990000000002, 23436.320000000000, 23437.119999999999]
    }

    book_cleaned = round(pd.DataFrame(data), 8)
    test_book = calculate_fees(book, 0, 0)
    test_book = round(clean_order_book(test_book), 8)
    assert test_book.equals(book_cleaned)


def test__update_filled_orders():
    data = {
    "Price": [23425.009999999998, 23426.119999999999, 23428.000000000000, 23431.580000000002,
            23433.490000000002, 23434.990000000002, 23436.320000000000, 23437.119999999999],
    "Quantity": [0.058000000000, 2.926000000000, 0.306396360000, 0.005000000000,
                1.926000000000, 0.010012010000, 0.005000000000, 5.023123010000],
    "Ask/Bid": ["Ask", "Ask", "Bid", "Ask", "Ask", "Bid", "Ask", "Bid"],
    "Exchange": ["Kraken", "Kraken", "Coinmetro", "Kraken", "Kraken", "Coinmetro", "Kraken", "Coinmetro"],
    "Fee": [0.000000000000, 0.000000000000, 0.000000000000, 0.000000000000,
            0.000000000000, 0.000000000000, 0.000000000000, 0.000000000000],
    "Net Price": [23425.009999999998, 23426.119999999999, 23428.000000000000, 23431.580000000002,
                23433.490000000002, 23434.990000000002, 23436.320000000000, 23437.119999999999]
    }
    book_cleaned = round(pd.DataFrame(data), 8)

    matched_orders_today_data = {
        "Price": [23426.119999999999, 23433.490000000002, 23436.320000000000],
        "Quantity": [2.926000000000, 1.926000000000, 0.005000000000],
        "Ask/Bid": ["Bid", "Ask", "Bid"],
        "Exchange": ["Kraken", "Kraken", "Coinmetro"],
        "Remaining Quantity": [2.000000000000, 1.000000000000, 0.002000000000],
    }
    matched_orders_today = round(pd.DataFrame(matched_orders_today_data), 8)
    data = {
    "Price": [23425.01, 23426.12, 23428.00, 23431.58, 23433.49, 23434.99, 23436.32, 23437.12],
    "Quantity": [0.058000, 2.926000, 0.30639636, 0.005000, 1.926000, 0.01001201, 0.005000, 5.02312301],
    "Ask/Bid": ["Ask", "Ask", "Bid", "Ask", "Ask", "Bid", "Ask", "Bid"],
    "Exchange": ["Kraken", "Kraken", "Coinmetro", "Kraken", "Kraken", "Coinmetro", "Kraken", "Coinmetro"],
    "Fee": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "Net Price": [23425.01, 23426.12, 23428.00, 23431.58, 23433.49, 23434.99, 23436.32, 23437.12],
    "Remaining Quantity": [0.058000, 2.000000, 0.30639636, 0.005000, 1.000000, 0.01001201, 0.005000, 5.02312301]
    }

    test_book = pd.DataFrame(data)
    pd.set_option('display.float_format', '{:.8f}'.format)

    # Print the actual and expected DataFrames
    actual = update_filled_orders(book_cleaned, matched_orders_today)
    print("Actual DataFrame:")
    print(actual)

    print("\nExpected DataFrame:")
    print(test_book)

    assert update_filled_orders(book_cleaned, matched_orders_today).equals(test_book)