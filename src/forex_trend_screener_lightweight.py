import sys
import os
import json
from datetime import datetime

# OANDA API credentials
access_token = "89c68ff389fa5e86dd30e8aff7c8935a-b0cb097b4475427f7be111d81e76c94b"
accountID = "101-004-31569953-001"

def create_log_entry(message):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def calculate_ema(prices, period):
    """Calculate EMA manually without pandas"""
    if len(prices) < period:
        return None
    
    # Simple EMA calculation
    multiplier = 2.0 / (period + 1.0)
    ema = prices[0]  # Start with first price
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def get_historical_data_simple(instrument, granularity, count):
    """Fetch data using requests directly"""
    import requests
    
    url = f"https://api-fxpractice.oanda.com/v3/instruments/{instrument}/candles"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "count": count,
        "granularity": granularity
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        create_log_entry(f"Error fetching data for {instrument}: {e}")
        return None

def process_pair(pair):
    """Process a single forex pair"""
    create_log_entry(f"Analyzing {pair}...")
    
    # Get daily data
    daily_data = get_historical_data_simple(pair, "D", 300)
    if not daily_data or 'candles' not in daily_data or len(daily_data['candles']) < 200:
        create_log_entry(f"Not enough daily data for {pair}")
        return None
    
    # Get hourly data
    hourly_data = get_historical_data_simple(pair, "H1", 300)
    if not hourly_data or 'candles' not in hourly_data or len(hourly_data['candles']) < 200:
        create_log_entry(f"Not enough hourly data for {pair}")
        return None
    
    # Extract closing prices
    daily_closes = [float(candle['mid']['c']) for candle in daily_data['candles']]
    hourly_closes = [float(candle['mid']['c']) for candle in hourly_data['candles']]
    
    # Calculate EMAs
    daily_ema_8 = calculate_ema(daily_closes, 8)
    daily_ema_50 = calculate_ema(daily_closes, 50)
    daily_ema_200 = calculate_ema(daily_closes, 200)
    
    hourly_ema_8 = calculate_ema(hourly_closes, 8)
    hourly_ema_50 = calculate_ema(hourly_closes, 50)
    hourly_ema_200 = calculate_ema(hourly_closes, 200)
    
    if None in [daily_ema_8, daily_ema_50, daily_ema_200, hourly_ema_8, hourly_ema_50, hourly_ema_200]:
        create_log_entry(f"Failed to calculate EMAs for {pair}")
        return None
    
    current_price = daily_closes[-1]
    
    # Check for trends
    result = {
        'pair': pair,
        'price': current_price,
        'daily_emas': [daily_ema_8, daily_ema_50, daily_ema_200],
        'hourly_emas': [hourly_ema_8, hourly_ema_50, hourly_ema_200],
        'long_trend': False,
        'short_trend': False
    }
    
    # Long trend: 8 > 50 > 200 and price > 8
    daily_long = daily_ema_8 > daily_ema_50 > daily_ema_200 and current_price > daily_ema_8
    hourly_long = hourly_ema_8 > hourly_ema_50 > hourly_ema_200 and current_price > hourly_ema_8
    
    if daily_long and hourly_long:
        result['long_trend'] = True
        create_log_entry(f"  -> {pair} added to long trending list")
    
    # Short trend: 200 > 50 > 8 and price < 8
    daily_short = daily_ema_200 > daily_ema_50 > daily_ema_8 and current_price < daily_ema_8
    hourly_short = hourly_ema_200 > hourly_ema_50 > hourly_ema_8 and current_price < hourly_ema_8
    
    if daily_short and hourly_short:
        result['short_trend'] = True
        create_log_entry(f"  -> {pair} added to short trending list")
    
    return result

def save_results_to_csv(results, filename):
    """Save results to CSV file"""
    try:
        with open(filename, 'w') as f:
            f.write("Pair,Price,Trend_Type,Daily_EMA_8,Daily_EMA_50,Daily_EMA_200,Hourly_EMA_8,Hourly_EMA_50,Hourly_EMA_200,Date\n")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for result in results:
                if result['long_trend']:
                    f.write(f"{result['pair']},{result['price']:.5f},Long,{result['daily_emas'][0]:.5f},{result['daily_emas'][1]:.5f},{result['daily_emas'][2]:.5f},{result['hourly_emas'][0]:.5f},{result['hourly_emas'][1]:.5f},{result['hourly_emas'][2]:.5f},{timestamp}\n")
                
                if result['short_trend']:
                    f.write(f"{result['pair']},{result['price']:.5f},Short,{result['daily_emas'][0]:.5f},{result['daily_emas'][1]:.5f},{result['daily_emas'][2]:.5f},{result['hourly_emas'][0]:.5f},{result['hourly_emas'][1]:.5f},{result['hourly_emas'][2]:.5f},{timestamp}\n")
        
        return True
    except Exception as e:
        create_log_entry(f"Error saving CSV: {e}")
        return False

def main():
    """Main function"""
    create_log_entry("Starting Forex Trend Screener (Lightweight Version)...")
    create_log_entry(f"Working directory: {os.getcwd()}")
    
    # Import requests here to avoid early import issues
    try:
        import requests
        create_log_entry("Successfully imported requests")
    except ImportError:
        create_log_entry("ERROR: requests module not available")
        input("Press Enter to exit...")
        return
    
    # List of forex pairs (reduced for testing)
    forex_pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"]
    
    results = []
    long_count = 0
    short_count = 0
    
    for pair in forex_pairs:
        result = process_pair(pair)
        if result:
            results.append(result)
            if result['long_trend']:
                long_count += 1
            if result['short_trend']:
                short_count += 1
    
    # Display results
    print("\n" + "="*60)
    print("                FOREX TREND ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nLong Trending Markets: {long_count}")
    for result in results:
        if result['long_trend']:
            print(f"  {result['pair']} - Price: {result['price']:.5f}")
    
    print(f"\nShort Trending Markets: {short_count}")
    for result in results:
        if result['short_trend']:
            print(f"  {result['pair']} - Price: {result['price']:.5f}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"forex_analysis_{timestamp}.csv"
    
    create_log_entry("Saving results to CSV...")
    if save_results_to_csv(results, csv_filename):
        create_log_entry(f"Results saved to {csv_filename}")
        print(f"\nResults saved to {csv_filename}")
    else:
        create_log_entry("Failed to save CSV file")
    
    print("="*60)
    create_log_entry("Analysis completed")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
