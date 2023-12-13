import pytest
import pandas as pd
from save_results import update_and_save_filled_orders, create_and_save_daily_profit_entry

@pytest.fixture
def sample_matched_orders_today():
    return pd.DataFrame({
        'Timestamp': ['2023-12-12 10:00:00', '2023-12-12 11:00:00'],
        'Profit': [100, 150],
        'Kraken BTC': [1.5, 2.0],
        'Kraken EUR': [500, 700],
        'Coinmetro BTC': [1.0, 1.5],
        'Coinmetro EUR': [300, 400]
    })

@pytest.fixture
def sample_matched_trades():
    return pd.DataFrame({
        'Timestamp': ['2023-12-12 12:00:00'],
        'Profit': [200],
        'Kraken BTC': [2.5],
        'Kraken EUR': [1000],
        'Coinmetro BTC': [2.0],
        'Coinmetro EUR': [600]
    })

@pytest.fixture
def sample_trades_today():
    return pd.DataFrame({
        'Timestamp': ['2023-12-12 10:00:00', '2023-12-12 11:00:00'],
        'Profit': [100, 150],
        'Kraken BTC': [1.5, 2.0],
        'Kraken EUR': [500, 700],
        'Coinmetro BTC': [1.0, 1.5],
        'Coinmetro EUR': [300, 400]
    })

def test_update_and_save_filled_orders(sample_matched_orders_today, sample_matched_trades, tmp_path):
    updated_orders = update_and_save_filled_orders(sample_matched_orders_today, sample_matched_trades, tmp_path)

    assert updated_orders.shape[0] == 3  # One more row added
    assert updated_orders.iloc[2]['Profit'] == 200  # Check if the new data is added

    # Check if the file is saved
    file_path = tmp_path / (pd.Timestamp.now().strftime("%Y-%m-%d") + ' matched_orders.xlsx')
    print("File path:", file_path)  # Add this line for debugging

    # Print the contents of the saved file
    saved_file_contents = pd.read_excel(file_path)
    print("Saved file contents:")
    print(saved_file_contents)

    assert file_path.is_file()

def test_create_and_save_daily_profit_entry(sample_trades_today, tmp_path):
    total_profit = 200
    kraken_btc_quantity = 2.5
    kraken_eur_quantity = 1000
    coinmetro_btc_quantity = 2.0
    coinmetro_eur_quantity = 600

    updated_trades = create_and_save_daily_profit_entry(sample_trades_today, total_profit, kraken_btc_quantity, kraken_eur_quantity, coinmetro_btc_quantity, coinmetro_eur_quantity, tmp_path)

    assert updated_trades.shape[0] == 3  # One more row added
    assert updated_trades.iloc[2]['Profit'] == 200  # Check if the new data is added

    # Check if the file is saved
    file_path = tmp_path / (pd.Timestamp.now().strftime("%Y-%m-%d") + ' trades.xlsx')
    assert file_path.is_file()