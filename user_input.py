"""
user_input.py

This is the file to ask user their input. Namely fee rates and the API speed limit (pause between data fetches)
"""

import time
from read_starting_info import fetch_kraken_taker_fee

MAX_ATTEMPTS = 3  # Set a maximum number of attempts

def get_user_input():
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        try:
            #coinmetro_fee = float(input("Enter Coinmetro fee percentage (e.g., 0.1 for 0.1%): ")) / 100
            #kraken_fee = float(input("Enter Kraken fee percentage (e.g., 0.24 for 0.24%): ")) / 100
            kraken_fee = fetch_kraken_taker_fee()
            sleep_duration = int(input("Enter interval duration in seconds (recommended 3): "))

            coinmetro_fee = 0.1 / 100
            print(f"coinmetro_fee: {coinmetro_fee * 100} %")
            print(f"kraken_fee: {kraken_fee * 100} %")
            print(f"sleep interval: {sleep_duration} s")
            print("User input - OK\n")

            time.sleep(1)
            return coinmetro_fee, kraken_fee, sleep_duration

        except ValueError:
            print("Invalid input. Please enter a valid number. (ValueError)")
            attempts += 1  # Increment the attempts counter
        except EOFError:
            print("\nScript terminated by user. (EOFError)")
            exit(1)  # You can change this to return default values or handle it differently based on your requirements.
    
    print("\nToo many incorrect values entered. Terminating code. (Error code 2)")
    exit(2)  # You can change this to return default values or handle it differently based on your requirements.
