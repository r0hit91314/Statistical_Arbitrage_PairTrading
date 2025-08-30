import os
from dotenv import load_dotenv
import pandas as pd
from upstox_client.rest import ApiException
import upstox_client
from data_fetching import get_instrument_key
from data_fetching import live_data
from order import exit_all_positions
from order import get_positions
import time
from datetime import datetime
import threading

path = os.path.abspath("acess_token.env")
load_dotenv(path)


access_token = os.getenv("ACCESS_TOKEN")
if not access_token:
    raise ValueError("ACCESS_TOKEN environment variable is not set.")


def run_pairs_trading(window  , hedge_ratio = 0.8173):
    # if you are buying selling 5 lots of y then you have to sell 5*hedge_ratio lots of x
    position = 0
    time.sleep(30)
    while True:

        df = pd.read_csv("live_data.csv")
        mean = df["spread"][-window: ].mean()
        std_dev = df["spread"][-window:].std()
        z_score = (df["spread"].iloc[-1] - mean)/std_dev
        print(f"for the price of y = {df["ticker1_y"].iloc[-1]} and x = {df["ticker2_x"].iloc[-1]} the z_score is: {z_score}")
        if z_score > 1 and position == 0:
            print("Enter Short Position")
            position = -1
        elif z_score < -1 and position == 0:
            print("Enter Long Position")
            position = 1
        elif abs(z_score < 0 and position == -1) or  (z_score > 0 and position == 1):
            print("Exit Position")
            exit_all_positions(access_token)
            current_position = get_positions(access_token)
            if len(current_position) == 0:
                print("All positions exited_woooo")
            else:
                print("Positions still open, retrying exit")
                while len(current_position) != 0:
                    exit_all_positions(access_token)
                    time.sleep(5)
                    current_position = get_positions(access_token)
                print("All positions exited")
            position = 0
        time.sleep(5)

    return 



if __name__ == "__main__":
    # Run both functions asynchronously
    t1 = threading.Thread(target=live_data("SBIN" , "HDFCBANK" , 0.8173), daemon=True)
    t2 = threading.Thread(target=run_pairs_trading, args=(5,), daemon=True)

    t1.start()
    t2.start()

    # Keep main thread alive
    t1.join()
    t2.join()    
