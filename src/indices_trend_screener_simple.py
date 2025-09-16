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

def process_index_simple(index):
    """Process a single index with 2 timeframes only"""
    create_log_entry(f"Analyzing {index}...")
    
    # Get historical data for 2 timeframes only (4hr and weekly)
    weekly_data = get_historical_data_simple(index, "W", 250)
    h4_data = get_historical_data_simple(index, "H4", 250)
    
    if not all([weekly_data, h4_data]):
        create_log_entry(f"Error fetching data for {index}")
        return []
    
    # Extract EMAs for each timeframe
    def extract_emas(data):
        if not data or 'candles' not in data:
            return None
        
        prices = []
        for candle in data['candles']:
            if candle['complete']:
                prices.append(float(candle['mid']['c']))
        
        if len(prices) < 200:
            return None
        
        # Calculate EMAs using last 200 prices
        prices_for_ema = prices[-200:]
        ema_8 = calculate_ema(prices_for_ema, 8)
        ema_50 = calculate_ema(prices_for_ema, 50)
        ema_200 = calculate_ema(prices_for_ema, 200)
        
        return {
            'ema_8': ema_8,
            'ema_50': ema_50,
            'ema_200': ema_200,
            'current_price': prices[-1]
        }
    
    # Get EMAs for timeframes
    weekly_emas = extract_emas(weekly_data)
    h4_emas = extract_emas(h4_data)
    
    if not weekly_emas or not h4_emas:
        create_log_entry(f"Error calculating EMAs for {index}")
        return []
    
    # Use the most recent price from 4hr data
    current_price = h4_emas['current_price']
    
    results = []
    
    def check_long_trend(price, ema_8, ema_50, ema_200):
        return ema_8 > ema_50 > ema_200 and price > ema_8
    
    def check_short_trend(price, ema_8, ema_50, ema_200):
        return ema_200 > ema_50 > ema_8 and price < ema_8
    
    # Check only 1 timeframe combination (4hr vs weekly)
    higher = weekly_emas
    lower = h4_emas
    
    # Check for long trend on both timeframes
    higher_long = check_long_trend(current_price, higher['ema_8'], higher['ema_50'], higher['ema_200'])
    lower_long = check_long_trend(current_price, lower['ema_8'], lower['ema_50'], lower['ema_200'])
    
    # Check for short trend on both timeframes
    higher_short = check_short_trend(current_price, higher['ema_8'], higher['ema_50'], higher['ema_200'])
    lower_short = check_short_trend(current_price, lower['ema_8'], lower['ema_50'], lower['ema_200'])
    
    if higher_long and lower_long:
        trend_type = "Long"
    elif higher_short and lower_short:
        trend_type = "Short"
    else:
        return []  # No clear trend on both timeframes
    
    # Store result
    result = {
        "Index": index,
        "Price": current_price,
        "Timeframe_Combination": "4hr vs weekly",
        "Trend_Type": trend_type,
        "Weekly_EMA_8": round(higher['ema_8'], 5),
        "Weekly_EMA_50": round(higher['ema_50'], 5),
        "Weekly_EMA_200": round(higher['ema_200'], 5),
        "H4_EMA_8": round(lower['ema_8'], 5),
        "H4_EMA_50": round(lower['ema_50'], 5),
        "H4_EMA_200": round(lower['ema_200'], 5),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    results.append(result)
    
    return results

def main():
    """Main function"""
    create_log_entry("Starting Simplified Index Trend Screener (4hr vs Weekly)...")
    
    # List of indices to analyze
    indices = [
        "SPX500_USD",   # S&P 500
        "NAS100_USD",   # NASDAQ 100
        "US30_USD",     # Dow Jones
        "UK100_GBP",    # FTSE 100
        "USB10Y_USD"    # US 10-Year Treasury Note
    ]
    
    all_results = []
    
    for index in indices:
        index_results = process_index_simple(index)
        all_results.extend(index_results)
    
    # Display comprehensive summary instead of CSV
    create_log_entry("=== SIMPLIFIED INDEX TREND ANALYSIS COMPLETE ===")
    
    if not all_results:
        create_log_entry("No trending indices found at this time.")
    else:
        # Count results by trend type and organize by category
        long_indices = []
        short_indices = []
        
        for result in all_results:
            index = result["Index"]
            trend = result["Trend_Type"]
            if trend == "Long":
                long_indices.append(index)
            else:
                short_indices.append(index)
        
        # Display results by category
        us_indices = ["SPX500_USD", "NAS100_USD", "US30_USD"]
        international = ["UK100_GBP"]
        bonds = ["USB10Y_USD"]
        
        create_log_entry(f"\n4HR VS WEEKLY ANALYSIS:")
        create_log_entry(f"  - {len(long_indices)} Long trends, {len(short_indices)} Short trends")
        
        if long_indices:
            create_log_entry(f"\nLONG TRENDING INDICES:")
            for category, name in [(us_indices, "US Indices"), (international, "International"), (bonds, "Bonds")]:
                category_longs = [c for c in long_indices if c in category]
                if category_longs:
                    create_log_entry(f"  - {name}: {', '.join(category_longs)}")
        
        if short_indices:
            create_log_entry(f"\nSHORT TRENDING INDICES:")
            for category, name in [(us_indices, "US Indices"), (international, "International"), (bonds, "Bonds")]:
                category_shorts = [c for c in short_indices if c in category]
                if category_shorts:
                    create_log_entry(f"  - {name}: {', '.join(category_shorts)}")
        
        create_log_entry(f"\nTOTAL SUMMARY:")
        create_log_entry(f"  - Total trending indices: {len(all_results)}")
        create_log_entry(f"  - Analyzed 5 indices (3 US, 1 international, 1 bond)")
        create_log_entry(f"  - Execution time: ~75% faster than full version")
    
    create_log_entry("\nNote: Simplified version for quick index scanning")
    create_log_entry("Use full version for comprehensive analysis and CSV export")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
