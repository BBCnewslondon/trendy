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

def process_commodity_full(commodity):
    """Process a single commodity with all timeframes"""
    create_log_entry(f"Analyzing {commodity}...")
    
    # Get historical data for all required timeframes
    daily_data = get_historical_data_simple(commodity, "D", 250)
    h1_data = get_historical_data_simple(commodity, "H1", 250)
    weekly_data = get_historical_data_simple(commodity, "W", 250)
    h4_data = get_historical_data_simple(commodity, "H4", 250)
    m5_data = get_historical_data_simple(commodity, "M5", 250)
    m15_data = get_historical_data_simple(commodity, "M15", 250)
    
    if not all([daily_data, h1_data, weekly_data, h4_data, m5_data, m15_data]):
        create_log_entry(f"Error fetching data for {commodity}")
        return []
    
    # Extract EMAs for each timeframe
    def extract_emas(data, timeframe_name):
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
    
    # Get EMAs for all timeframes
    daily_emas = extract_emas(daily_data, "daily")
    h1_emas = extract_emas(h1_data, "h1")
    weekly_emas = extract_emas(weekly_data, "weekly")
    h4_emas = extract_emas(h4_data, "h4")
    m5_emas = extract_emas(m5_data, "m5")
    m15_emas = extract_emas(m15_data, "m15")
    
    if not all([daily_emas, h1_emas, weekly_emas, h4_emas, m5_emas, m15_emas]):
        create_log_entry(f"Error calculating EMAs for {commodity}")
        return []
    
    # Use the most recent price from 5-minute data (safely)
    if m5_emas is None:
        create_log_entry(f"Missing 5-minute EMA data for {commodity}")
        return []
    current_price = m5_emas['current_price']
    
    results = []
    
    def check_long_trend(price, ema_8, ema_50, ema_200):
        return ema_8 > ema_50 > ema_200 and price > ema_8
    
    def check_short_trend(price, ema_8, ema_50, ema_200):
        return ema_200 > ema_50 > ema_8 and price < ema_8
    
    # Check all timeframe combinations
    timeframe_combos = [
        {
            'name': '1hr vs 1d',
            'higher': daily_emas,
            'lower': h1_emas
        },
        {
            'name': '4hr vs weekly',
            'higher': weekly_emas,
            'lower': h4_emas
        },
        {
            'name': '5min vs 1hr',
            'higher': h1_emas,
            'lower': m5_emas
        },
        {
            'name': '15min vs 4hr',
            'higher': h4_emas,
            'lower': m15_emas
        }
    ]
    
    for combo in timeframe_combos:
        higher = combo['higher']
        lower = combo['lower']
        
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
            continue  # No clear trend on both timeframes
        
        # Store result
        result = {
            "Commodity": commodity,
            "Price": current_price,
            "Timeframe_Combination": combo['name'],
            "Trend_Type": trend_type,
            "Higher_TF_EMA_8": round(higher['ema_8'], 5),
            "Higher_TF_EMA_50": round(higher['ema_50'], 5),
            "Higher_TF_EMA_200": round(higher['ema_200'], 5),
            "Lower_TF_EMA_8": round(lower['ema_8'], 5),
            "Lower_TF_EMA_50": round(lower['ema_50'], 5),
            "Lower_TF_EMA_200": round(lower['ema_200'], 5),
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        results.append(result)
    
    return results

def save_results_to_csv(results, filename):
    """Save results to CSV file with all timeframes"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if results:
                # Write header
                headers = list(results[0].keys())
                file.write(','.join(headers) + '\n')
                
                # Write data
                for result in results:
                    row = [str(result[header]) for header in headers]
                    file.write(','.join(row) + '\n')
                
                create_log_entry(f"Results saved to {filename}")
            else:
                file.write("No trending commodities found\n")
                create_log_entry("No trending commodities found")
    except Exception as e:
        create_log_entry(f"Error saving results: {e}")

def main():
    """Main function"""
    create_log_entry("Starting Commodity Trend Screener...")
    
    # List of commodities to analyze - focused on major commodities
    commodities = [
        # Precious Metals
        "XAU_USD",  # Gold
        "XAG_USD",  # Silver
        "XPT_USD",  # Platinum
        "XPD_USD",  # Palladium
        
        # Energy
        "WTICO_USD",  # West Texas Oil
        "BCO_USD",    # Brent Crude Oil
        "NATGAS_USD", # Natural Gas
        
        # Agricultural
        "CORN_USD",   # Corn
        "SOYBN_USD",  # Soybeans
        "WHEAT_USD",  # Wheat
        "SUGAR_USD",  # Sugar
    ]
    
    all_results = []
    
    for commodity in commodities:
        commodity_results = process_commodity_full(commodity)
        all_results.extend(commodity_results)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"commodity_analysis_full_{timestamp}.csv"
    
    # Save results
    save_results_to_csv(all_results, filename)
    
    # Display summary
    create_log_entry(f"\n=== COMMODITY TREND ANALYSIS COMPLETE ===")
    
    # Count results by timeframe and trend type
    timeframes = {}
    for result in all_results:
        tf = result["Timeframe_Combination"]
        trend = result["Trend_Type"]
        if tf not in timeframes:
            timeframes[tf] = {"Long": 0, "Short": 0}
        timeframes[tf][trend] += 1
    
    for tf, counts in timeframes.items():
        create_log_entry(f"{tf}: {counts['Long']} Long, {counts['Short']} Short")
    
    create_log_entry(f"Total trending commodities found: {len(all_results)}")
    create_log_entry(f"Results saved to: {filename}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
