import pandas as pd
import os
from unittest.mock import patch
from pandas.testing import assert_frame_equal
import pytest
from read_files import initialize_matched_orders_today, initialize_trades_today

@pytest.fixture
def temp_directory(tmpdir):
    return str(tmpdir.mkdir('test_data'))

def test_initialize_matched_orders_today_with_existing_file(temp_directory):
    # Create a temporary file path within the temporary directory
    test_file_path = os.path.join(temp_directory, pd.Timestamp.now().strftime("%Y-%m-%d") + ' matched_orders.xlsx')
    # Create a sample DataFrame with specific columns
    data = {
        'Timestamp': [],
        'Price': [],
        'Quantity': [],
        'Ask/Bid': [],
        'Exchange': [],
        'Fee': [],
        'Net Price': [],
        'Matched Quantity': [],
        'Remaining Quantity': []
    }
    # Save the DataFrame to an Excel file
    pd.DataFrame(data).to_excel(test_file_path, index=False)
    
    with patch('pandas.read_excel') as mock_read_excel:
        # Mock the read_excel function to return an empty DataFrame
        mock_read_excel.return_value = pd.DataFrame()
        print(f"expected result: {mock_read_excel.return_value}")
        
        # Call the function being tested
        result = initialize_matched_orders_today(temp_directory)
        print(f"result: {result}")
    
    # Assert that the read_excel function was called exactly once with the correct file path
    mock_read_excel.assert_called_once_with(test_file_path)
    
    # Assert that the result is an empty DataFrame with the expected columns
    expected_result = pd.DataFrame(columns=['Timestamp', 'Price', 'Quantity', 'Ask/Bid', 'Exchange', 'Fee', 'Net Price', 'Matched Quantity', 'Remaining Quantity'])
    assert_frame_equal(result, expected_result)


def test_initialize_matched_orders_today_nonexistent_file(temp_directory):
    with patch('pandas.read_excel') as mock_read_excel:
        # Mock the read_excel function to raise a FileNotFoundError
        mock_read_excel.side_effect = FileNotFoundError

        result = initialize_matched_orders_today(temp_directory)

        # Assert that the result is an empty DataFrame with the expected columns
        assert result.empty
        assert result.columns.tolist() == ['Timestamp', 'Price', 'Quantity', 'Ask/Bid', 'Exchange', 'Fee', 'Net Price', 'Matched Quantity', 'Remaining Quantity']


def test_initialize_trades_today_existing_file(temp_directory):
    # Create a temporary file for testing
    test_file_path = os.path.join(temp_directory, pd.Timestamp.now().strftime("%Y-%m-%d") + ' trades.xlsx')
    pd.DataFrame().to_excel(test_file_path, index=False)

    with patch('pandas.read_excel') as mock_read_excel:
        # Mock the read_excel function to return an empty DataFrame
        mock_read_excel.return_value = pd.DataFrame()

        result = initialize_trades_today(temp_directory)

        # Assert that the read_excel function was called with the correct file path
        mock_read_excel.assert_called_with(test_file_path)

        # Check if the result is an empty DataFrame
        assert result.empty

        # If not empty, assert the columns
        if not result.empty:
            assert result.columns.tolist() == ['Timestamp', 'Profit', 'Kraken BTC', 'Kraken EUR', 'Coinmetro BTC', 'Coinmetro EUR']


def test_initialize_trades_today_nonexistent_file(temp_directory):
    with patch('pandas.read_excel') as mock_read_excel:
        # Mock the read_excel function to raise a FileNotFoundError
        mock_read_excel.side_effect = FileNotFoundError

        result = initialize_trades_today(temp_directory)

        # Assert that the result is an empty DataFrame with the expected columns
        assert result.empty
        assert result.columns.tolist() == ['Timestamp', 'Profit', 'Kraken BTC', 'Kraken EUR', 'Coinmetro BTC', 'Coinmetro EUR']
