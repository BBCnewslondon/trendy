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

def process_pair_full(pair):
    """Process a single forex pair with all timeframes"""
    create_log_entry(f"Analyzing {pair}...")
    
    # Get data for all timeframes
    timeframes = {
        'daily': 'D',
        'weekly': 'W', 
        'h4': 'H4',
        'h1': 'H1',
        'm15': 'M15',
        'm5': 'M5'
    }
    
    data = {}
    
    # Fetch all timeframe data
    for tf_name, tf_code in timeframes.items():
        tf_data = get_historical_data_simple(pair, tf_code, 300)
        if not tf_data or 'candles' not in tf_data or len(tf_data['candles']) < 200:
            create_log_entry(f"Not enough {tf_name} data for {pair}")
            return None
        data[tf_name] = tf_data
    
    # Extract closing prices for all timeframes
    closes = {}
    for tf_name, tf_data in data.items():
        closes[tf_name] = [float(candle['mid']['c']) for candle in tf_data['candles']]
    
    # Calculate EMAs for all timeframes
    emas = {}
    for tf_name, prices in closes.items():
        emas[tf_name] = {
            'ema_8': calculate_ema(prices, 8),
            'ema_50': calculate_ema(prices, 50),
            'ema_200': calculate_ema(prices, 200)
        }
        
        # Check if any EMA calculation failed
        if None in emas[tf_name].values():
            create_log_entry(f"Failed to calculate EMAs for {pair} {tf_name}")
            return None
    
    current_price = closes['daily'][-1]
    
    # Check trends for all timeframe combinations
    result = {
        'pair': pair,
        'price': current_price,
        'emas': emas,
        'trends': {
            'long_1hr_1d': False,
            'short_1hr_1d': False,
            'long_4hr_weekly': False,
            'short_4hr_weekly': False,
            'long_5min_1hr': False,
            'short_5min_1hr': False,
            'long_15min_4hr': False,
            'short_15min_4hr': False
        }
    }
    
    def check_long_trend(price, ema_8, ema_50, ema_200):
        return ema_8 > ema_50 > ema_200 and price > ema_8
    
    def check_short_trend(price, ema_8, ema_50, ema_200):
        return ema_200 > ema_50 > ema_8 and price < ema_8
    
    # 1. Check 1hr vs 1d timeframes
    daily_emas = emas['daily']
    h1_emas = emas['h1']
    
    daily_long = check_long_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200'])
    h1_long = check_long_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200'])
    
    if daily_long and h1_long:
        result['trends']['long_1hr_1d'] = True
        create_log_entry(f"  -> {pair} added to long trending [1hr,1d] list")
    
    daily_short = check_short_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200'])
    h1_short = check_short_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200'])
    
    if daily_short and h1_short:
        result['trends']['short_1hr_1d'] = True
        create_log_entry(f"  -> {pair} added to short trending [1hr,1d] list")
    
    # 2. Check 4hr vs weekly timeframes
    weekly_emas = emas['weekly']
    h4_emas = emas['h4']
    
    weekly_long = check_long_trend(current_price, weekly_emas['ema_8'], weekly_emas['ema_50'], weekly_emas['ema_200'])
    h4_long = check_long_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200'])
    
    if weekly_long and h4_long:
        result['trends']['long_4hr_weekly'] = True
        create_log_entry(f"  -> {pair} added to long trending [4hr,weekly] list")
    
    weekly_short = check_short_trend(current_price, weekly_emas['ema_8'], weekly_emas['ema_50'], weekly_emas['ema_200'])
    h4_short = check_short_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200'])
    
    if weekly_short and h4_short:
        result['trends']['short_4hr_weekly'] = True
        create_log_entry(f"  -> {pair} added to short trending [4hr,weekly] list")
    
    # 3. Check 5min vs 1hr timeframes
    m5_emas = emas['m5']
    
    h1_long_5m = check_long_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200'])
    m5_long = check_long_trend(current_price, m5_emas['ema_8'], m5_emas['ema_50'], m5_emas['ema_200'])
    
    if h1_long_5m and m5_long:
        result['trends']['long_5min_1hr'] = True
        create_log_entry(f"  -> {pair} added to long trending [5min,1hr] list")
    
    h1_short_5m = check_short_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200'])
    m5_short = check_short_trend(current_price, m5_emas['ema_8'], m5_emas['ema_50'], m5_emas['ema_200'])
    
    if h1_short_5m and m5_short:
        result['trends']['short_5min_1hr'] = True
        create_log_entry(f"  -> {pair} added to short trending [5min,1hr] list")
    
    # 4. Check 15min vs 4hr timeframes
    m15_emas = emas['m15']
    
    h4_long_15m = check_long_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200'])
    m15_long = check_long_trend(current_price, m15_emas['ema_8'], m15_emas['ema_50'], m15_emas['ema_200'])
    
    if h4_long_15m and m15_long:
        result['trends']['long_15min_4hr'] = True
        create_log_entry(f"  -> {pair} added to long trending [15min,4hr] list")
    
    h4_short_15m = check_short_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200'])
    m15_short = check_short_trend(current_price, m15_emas['ema_8'], m15_emas['ema_50'], m15_emas['ema_200'])
    
    if h4_short_15m and m15_short:
        result['trends']['short_15min_4hr'] = True
        create_log_entry(f"  -> {pair} added to short trending [15min,4hr] list")
    
    return result

def save_results_to_csv(results, filename):
    """Save results to CSV file with all timeframes"""
    try:
        with open(filename, 'w') as f:
            f.write("Pair,Price,Timeframe_Combination,Trend_Type,Higher_TF_EMA_8,Higher_TF_EMA_50,Higher_TF_EMA_200,Lower_TF_EMA_8,Lower_TF_EMA_50,Lower_TF_EMA_200,Date\n")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            timeframe_mappings = {
                'long_1hr_1d': ('1hr vs 1d', 'Long', 'daily', 'h1'),
                'short_1hr_1d': ('1hr vs 1d', 'Short', 'daily', 'h1'),
                'long_4hr_weekly': ('4hr vs weekly', 'Long', 'weekly', 'h4'),
                'short_4hr_weekly': ('4hr vs weekly', 'Short', 'weekly', 'h4'),
                'long_5min_1hr': ('5min vs 1hr', 'Long', 'h1', 'm5'),
                'short_5min_1hr': ('5min vs 1hr', 'Short', 'h1', 'm5'),
                'long_15min_4hr': ('15min vs 4hr', 'Long', 'h4', 'm15'),
                'short_15min_4hr': ('15min vs 4hr', 'Short', 'h4', 'm15')
            }
            
            for result in results:
                for trend_key, is_trending in result['trends'].items():
                    if is_trending:
                        tf_combo, trend_type, higher_tf, lower_tf = timeframe_mappings[trend_key]
                        higher_emas = result['emas'][higher_tf]
                        lower_emas = result['emas'][lower_tf]
                        
                        f.write(f"{result['pair']},{result['price']:.5f},{tf_combo},{trend_type},"
                               f"{higher_emas['ema_8']:.5f},{higher_emas['ema_50']:.5f},{higher_emas['ema_200']:.5f},"
                               f"{lower_emas['ema_8']:.5f},{lower_emas['ema_50']:.5f},{lower_emas['ema_200']:.5f},"
                               f"{timestamp}\n")
        
        return True
    except Exception as e:
        create_log_entry(f"Error saving CSV: {e}")
        return False

def main():
    """Main function"""
    create_log_entry("Starting Forex Trend Screener (Full Multi-Timeframe Version)...")
    create_log_entry(f"Working directory: {os.getcwd()}")
    
    # Import requests here to avoid early import issues
    try:
        import requests
        create_log_entry("Successfully imported requests")
    except ImportError:
        create_log_entry("ERROR: requests module not available")
        input("Press Enter to exit...")
        return
    
    # List of forex pairs - all 28 pairs
    forex_pairs = [
        # Major pairs
        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "USD_CAD", "AUD_USD", "NZD_USD",
        
        # Minor pairs (Cross currency pairs)
        "EUR_GBP", "EUR_JPY", "EUR_CHF", "EUR_CAD", "EUR_AUD", "EUR_NZD",
        "GBP_JPY", "GBP_CHF", "GBP_CAD", "GBP_AUD", "GBP_NZD",
        "CHF_JPY", "CAD_CHF", "CAD_JPY", "AUD_CHF", "AUD_JPY", "AUD_CAD", "AUD_NZD",
        "NZD_CHF", "NZD_JPY", "NZD_CAD"
    ]
    
    results = []
    counts = {
        'long_1hr_1d': 0,
        'short_1hr_1d': 0,
        'long_4hr_weekly': 0,
        'short_4hr_weekly': 0,
        'long_5min_1hr': 0,
        'short_5min_1hr': 0,
        'long_15min_4hr': 0,
        'short_15min_4hr': 0
    }
    
    for pair in forex_pairs:
        result = process_pair_full(pair)
        if result:
            results.append(result)
            for trend_key, is_trending in result['trends'].items():
                if is_trending:
                    counts[trend_key] += 1
    
    # Display results
    print("\n" + "="*60)
    print("                FOREX TREND ANALYSIS RESULTS")
    print("="*60)
    
    trend_labels = {
        'long_1hr_1d': 'Long Trending Markets [1hr,1d]',
        'short_1hr_1d': 'Short Trending Markets [1hr,1d]',
        'long_4hr_weekly': 'Long Trending Markets [4hr,weekly]',
        'short_4hr_weekly': 'Short Trending Markets [4hr,weekly]',
        'long_5min_1hr': 'Long Trending Markets [5min,1hr]',
        'short_5min_1hr': 'Short Trending Markets [5min,1hr]',
        'long_15min_4hr': 'Long Trending Markets [15min,4hr]',
        'short_15min_4hr': 'Short Trending Markets [15min,4hr]'
    }
    
    for trend_key, label in trend_labels.items():
        print(f"\n{label}: {counts[trend_key]}")
        for result in results:
            if result['trends'][trend_key]:
                print(f"  {result['pair']} - Price: {result['price']:.5f}")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"forex_analysis_full_{timestamp}.csv"
    
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
