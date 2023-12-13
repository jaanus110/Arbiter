# test__data_fetch.py

import asyncio
import pytest
from data_fetch import get_orderbooks


@pytest.mark.asyncio
async def test__get_orderbooks__response_is_lists():
    try:
        coinmetro_bids, coinmetro_asks, kraken_bids, kraken_asks = await get_orderbooks()
        assert isinstance(coinmetro_bids, list), f"Expected coinmetro_bids to be a tuple, got {type(coinmetro_bids)}"
        assert isinstance(coinmetro_asks, list), f"Expected coinmetro_asks to be a tuple, got {type(coinmetro_asks)}"
        assert isinstance(kraken_bids, list), f"Expected kraken_bids to be a tuple, got {type(kraken_bids)}"
        assert isinstance(kraken_asks, list), f"Expected kraken_asks to be a tuple, got {type(kraken_asks)}"

    except Exception as e:
        print(f"An error occurred: {str(e)}")


@pytest.mark.asyncio
async def test__get_orderbooks__response_is_not_empty():
    try:
        coinmetro_bids, coinmetro_asks, kraken_bids, kraken_asks = await get_orderbooks()
        assert coinmetro_bids, "Coinmetro bids are empty"
        assert coinmetro_asks, "Coinmetro asks are empty"
        assert kraken_bids, "Kraken bids are empty"
        assert kraken_asks, "Kraken asks are empty"

    except Exception as e:
        print(f"An error occurred: {str(e)}")


@pytest.mark.asyncio
async def test__get_orderbooks__response_structure():
    coinmetro_bids, coinmetro_asks, kraken_bids, kraken_asks = await get_orderbooks()

    # Test Coinmetro bids
    for price, quantity in coinmetro_bids:
        float_price = float(price)
        float_quantity = float(quantity)
        assert isinstance(float_price, float)
        assert isinstance(float_quantity, float)

    # Test Coinmetro asks
    for price, quantity in coinmetro_asks:
        float_price = float(price)
        float_quantity = float(quantity)
        assert isinstance(float_price, float)
        assert isinstance(float_quantity, float)

    # Test Kraken bids
    for price, quantity, timestamp in kraken_bids:
        float_price = float(price)
        float_quantity = float(quantity)
        assert isinstance(float_price, float)
        assert isinstance(float_quantity, float)

    # Test Kraken asks
    for price, quantity, timestamp in kraken_asks:
        float_price = float(price)
        float_quantity = float(quantity)
        assert isinstance(float_price, float)
        assert isinstance(float_quantity, float)
