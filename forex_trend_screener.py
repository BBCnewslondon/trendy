import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from datetime import datetime

# OANDA API credentials
access_token = "YOUR_ACCESS_TOKEN"
accountID = "YOUR_ACCOUNT_ID"
api = oandapyV20.API(access_token=access_token, environment="practice")

# List of forex pairs to check
# A smaller list for testing purposes
forex_pairs = [
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD",
    "USD_CHF", "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY"
]

def get_historical_data(instrument, granularity, count):
    """Fetches historical data for a given instrument."""
    params = {
        "count": count,
        "granularity": granularity
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    api.request(r)
    return r.response

def calculate_emas(data):
    """Calculates 8, 50, and 200 EMAs."""
    df = pd.DataFrame([
        {
            "time": candle['time'],
            "close": float(candle['mid']['c'])
        } for candle in data['candles']
    ])
    df['ema_8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
    return df.iloc[-1]

def check_long_trend(price, ema_8, ema_50, ema_200):
    """Checks for a long trend condition."""
    return ema_8 > ema_50 > ema_200 and price > ema_8

def check_short_trend(price, ema_8, ema_50, ema_200):
    """Checks for a short trend condition."""
    return ema_200 > ema_50 > ema_8 and price < ema_8

def main():
    """Main function to run the forex trend screener."""
    long_trending = []
    short_trending = []
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for pair in forex_pairs:
        print(f"Analyzing {pair}...")
        try:
            # Get daily data
            daily_data = get_historical_data(pair, "D", 300)
            if not daily_data or 'candles' not in daily_data or len(daily_data['candles']) < 200:
                print(f"Not enough daily data for {pair}")
                continue
            
            daily_emas = calculate_emas(daily_data)
            current_price = float(daily_data['candles'][-1]['mid']['c'])

            # Get hourly data
            hourly_data = get_historical_data(pair, "H1", 300)
            if not hourly_data or 'candles' not in hourly_data or len(hourly_data['candles']) < 200:
                print(f"Not enough hourly data for {pair}")
                continue
            
            hourly_emas = calculate_emas(hourly_data)
            
            # Check for long trend
            if check_long_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                if check_long_trend(current_price, hourly_emas['ema_8'], hourly_emas['ema_50'], hourly_emas['ema_200']):
                    long_trending.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to long trending list.")

            # Check for short trend
            if check_short_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                if check_short_trend(current_price, hourly_emas['ema_8'], hourly_emas['ema_50'], hourly_emas['ema_200']):
                    short_trending.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to short trending list.")

        except Exception as e:
            print(f"An error occurred for {pair}: {e}")

    print("\n--- Results ---")
    print("\nLong Trending Markets:")
    for item in long_trending:
        print(item)

    print("\nShort Trending Markets:")
    for item in short_trending:
        print(item)

if __name__ == "__main__":
    main()
