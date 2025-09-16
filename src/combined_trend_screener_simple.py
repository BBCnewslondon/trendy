"""
Combined Simplified Trend Screener - All Markets Analysis
Analyzes Forex, Commodities, and Indices using 1hr vs 1day timeframe combination
Includes German 40 (GER40_EUR) as requested
"""

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

def process_instrument(instrument, instrument_type):
    """Process a single instrument with 1hr vs 1day timeframe"""
    create_log_entry(f"Analyzing {instrument}...")
    
    # Get historical data for 1hr and 1day timeframes
    daily_data = get_historical_data_simple(instrument, "D", 250)
    h1_data = get_historical_data_simple(instrument, "H1", 250)
    
    if not all([daily_data, h1_data]):
        create_log_entry(f"Error fetching data for {instrument}")
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
    daily_emas = extract_emas(daily_data)
    h1_emas = extract_emas(h1_data)
    
    if not daily_emas or not h1_emas:
        create_log_entry(f"Error calculating EMAs for {instrument}")
        return []
    
    # Use the most recent price from hourly data
    current_price = h1_emas['current_price']
    
    results = []
    
    def check_long_trend(price, ema_8, ema_50, ema_200):
        return ema_8 > ema_50 > ema_200 and price > ema_8
    
    def check_short_trend(price, ema_8, ema_50, ema_200):
        return ema_200 > ema_50 > ema_8 and price < ema_8
    
    # Check 1hr vs 1day timeframe combination
    higher = daily_emas
    lower = h1_emas
    
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
        "Instrument": instrument,
        "Type": instrument_type,
        "Price": current_price,
        "Timeframe_Combination": "1hr vs 1d",
        "Trend_Type": trend_type,
        "Daily_EMA_8": round(higher['ema_8'], 5),
        "Daily_EMA_50": round(higher['ema_50'], 5),
        "Daily_EMA_200": round(higher['ema_200'], 5),
        "H1_EMA_8": round(lower['ema_8'], 5),
        "H1_EMA_50": round(lower['ema_50'], 5),
        "H1_EMA_200": round(lower['ema_200'], 5),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    results.append(result)
    
    return results

def main():
    """Main function"""
    create_log_entry("Starting Combined Simplified Trend Screener (1hr vs 1day)...")
    
    # Define all instruments by category
    forex_pairs = [
        # Major pairs
        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "USD_CAD", "AUD_USD", "NZD_USD",
        
        # Minor pairs (Cross currency pairs)
        "EUR_GBP", "EUR_JPY", "EUR_CHF", "EUR_CAD", "EUR_AUD", "EUR_NZD",
        "GBP_JPY", "GBP_CHF", "GBP_CAD", "GBP_AUD", "GBP_NZD",
        "CHF_JPY", "CAD_CHF", "CAD_JPY", "AUD_CHF", "AUD_JPY", "AUD_CAD", "AUD_NZD",
        "NZD_CHF", "NZD_JPY", "NZD_CAD"
    ]
    
    commodities = [
        # Precious Metals
        "XAU_USD",  # Gold
        "XAG_USD",  # Silver
        "XPT_USD",  # Platinum
        "XPD_USD",  # Palladium
        
        # Energy
        "BCO_USD",  # Brent Crude Oil
        "WTICO_USD", # West Texas Intermediate Crude Oil
        "NATGAS_USD", # Natural Gas
        
        # Agricultural
        "CORN_USD",  # Corn
        "WHEAT_USD", # Wheat
        "SOYBN_USD", # Soybeans
        "SUGAR_USD"  # Sugar
    ]
    
    indices = [
        "SPX500_USD",   # S&P 500
        "NAS100_USD",   # NASDAQ 100
        "US30_USD",     # Dow Jones
        "UK100_GBP",    # FTSE 100
        "DE30_EUR",     # German 30 (DAX) - Corrected symbol
        "USB10Y_USD"    # US 10-Year Treasury Note
    ]
    
    all_results = []
    
    # Process Forex pairs
    create_log_entry("\n=== ANALYZING FOREX PAIRS ===")
    forex_results = []
    for pair in forex_pairs:
        pair_results = process_instrument(pair, "Forex")
        forex_results.extend(pair_results)
        all_results.extend(pair_results)
    
    # Process Commodities
    create_log_entry("\n=== ANALYZING COMMODITIES ===")
    commodity_results = []
    for commodity in commodities:
        commodity_results_temp = process_instrument(commodity, "Commodity")
        commodity_results.extend(commodity_results_temp)
        all_results.extend(commodity_results_temp)
    
    # Process Indices
    create_log_entry("\n=== ANALYZING INDICES ===")
    index_results = []
    for index in indices:
        index_results_temp = process_instrument(index, "Index")
        index_results.extend(index_results_temp)
        all_results.extend(index_results_temp)
    
    # Display comprehensive summary (matching comprehensive scripts style)
    create_log_entry("\n=== COMBINED TREND ANALYSIS COMPLETE ===")
    
    # Display results using comprehensive format (like forex_trend_screener_fixed.py)
    print("\n" + "="*60)
    print("            COMBINED TREND ANALYSIS RESULTS")
    print("="*60)
    
    if not all_results:
        print("\nNo trending instruments found at this time.")
    else:
        # Count results by instrument type and trend type
        forex_long = [r for r in forex_results if r["Trend_Type"] == "Long"]
        forex_short = [r for r in forex_results if r["Trend_Type"] == "Short"]
        commodity_long = [r for r in commodity_results if r["Trend_Type"] == "Long"]
        commodity_short = [r for r in commodity_results if r["Trend_Type"] == "Short"]
        index_long = [r for r in index_results if r["Trend_Type"] == "Long"]
        index_short = [r for r in index_results if r["Trend_Type"] == "Short"]
        
        # Collect all trending instruments for detailed display
        all_long_results = forex_long + commodity_long + index_long
        all_short_results = forex_short + commodity_short + index_short
        
        trend_labels = {
            'long_1hr_1d': 'Long Trending Markets [1hr,1d]',
            'short_1hr_1d': 'Short Trending Markets [1hr,1d]'
        }
        
        # Display long trending instruments with prices
        if all_long_results:
            print(f"\n{trend_labels['long_1hr_1d']}: {len(all_long_results)}")
            for result in all_long_results:
                print(f"  {result['Instrument']} - Price: {result['Price']:.5f}")
        
        # Display short trending instruments with prices
        if all_short_results:
            print(f"\n{trend_labels['short_1hr_1d']}: {len(all_short_results)}")
            for result in all_short_results:
                print(f"  {result['Instrument']} - Price: {result['Price']:.5f}")
        
        print("\n" + "="*60)
        print("MARKET BREAKDOWN:")
        print(f"  - Forex pairs analyzed: 28 (Long: {len(forex_long)}, Short: {len(forex_short)})")
        print(f"  - Commodities analyzed: 11 (Long: {len(commodity_long)}, Short: {len(commodity_short)})")
        print(f"  - Indices analyzed: 6 (Long: {len(index_long)}, Short: {len(index_short)})")
        print(f"  - Total trending instruments: {len(all_results)}")
        print(f"  - Timeframe combination: 1hr vs 1day")
        print("="*60)
    
    create_log_entry("\nNote: Combined simplified version for comprehensive market scanning")
    create_log_entry("Analyzes all major markets with single timeframe combination for efficiency")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
