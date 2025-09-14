import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from datetime import datetime

# OANDA API credentials
access_token = "89c68ff389fa5e86dd30e8aff7c8935a-b0cb097b4475427f7be111d81e76c94b"
accountID = "101-004-31569953-001"
api = oandapyV20.API(access_token=access_token, environment="practice")

# Smaller list for quick testing
forex_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]

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

def export_to_excel(long_1hr_1d, short_1hr_1d, long_4hr_weekly, short_4hr_weekly,
                   long_5min_1hr, short_5min_1hr, long_15min_4hr, short_15min_4hr, run_date):
    """Export all trending markets to an Excel file."""
    
    # Create a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forex_trend_analysis_{timestamp}.xlsx"
    
    # Create DataFrames for each category
    datasets = {
        'Long 1hr vs 1d': pd.DataFrame(long_1hr_1d),
        'Short 1hr vs 1d': pd.DataFrame(short_1hr_1d),
        'Long 4hr vs weekly': pd.DataFrame(long_4hr_weekly),
        'Short 4hr vs weekly': pd.DataFrame(short_4hr_weekly),
        'Long 5min vs 1hr': pd.DataFrame(long_5min_1hr),
        'Short 5min vs 1hr': pd.DataFrame(short_5min_1hr),
        'Long 15min vs 4hr': pd.DataFrame(long_15min_4hr),
        'Short 15min vs 4hr': pd.DataFrame(short_15min_4hr)
    }
    
    # Create Excel writer object
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Create summary sheet
        summary_data = []
        for sheet_name, df in datasets.items():
            count = len(df) if not df.empty else 0
            summary_data.append({
                'Category': sheet_name,
                'Count': count,
                'Pairs': ', '.join(df['pair'].tolist()) if not df.empty else 'None'
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create individual sheets for each category
        for sheet_name, df in datasets.items():
            if not df.empty:
                # Add some additional columns for analysis
                df_export = df.copy()
                df_export['timeframe_combination'] = sheet_name
                df_export.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Create empty sheet with headers
                empty_df = pd.DataFrame(columns=['pair', 'date', 'timeframe_combination'])
                empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Create a combined sheet with all results
        all_data = []
        for sheet_name, df in datasets.items():
            if not df.empty:
                df_temp = df.copy()
                df_temp['category'] = sheet_name
                all_data.append(df_temp)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_excel(writer, sheet_name='All Results', index=False)
    
    return filename

def main():
    """Main function to run the forex trend screener."""
    # Initialize lists for different timeframe combinations
    long_trending_1hr_1d = []
    short_trending_1hr_1d = []
    long_trending_4hr_weekly = []
    short_trending_4hr_weekly = []
    long_trending_5min_1hr = []
    short_trending_5min_1hr = []
    long_trending_15min_4hr = []
    short_trending_15min_4hr = []
    
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for pair in forex_pairs:
        print(f"Analyzing {pair}...")
        try:
            # Get data for all timeframes
            daily_data = get_historical_data(pair, "D", 300)
            weekly_data = get_historical_data(pair, "W", 300)
            h4_data = get_historical_data(pair, "H4", 300)
            h1_data = get_historical_data(pair, "H1", 300)
            m15_data = get_historical_data(pair, "M15", 300)
            m5_data = get_historical_data(pair, "M5", 300)
            
            # Check if we have enough data for all timeframes
            timeframes = {
                "daily": daily_data,
                "weekly": weekly_data,
                "4hr": h4_data,
                "1hr": h1_data,
                "15min": m15_data,
                "5min": m5_data
            }
            
            # Skip if any timeframe doesn't have enough data
            skip_pair = False
            for tf_name, tf_data in timeframes.items():
                if not tf_data or 'candles' not in tf_data or len(tf_data['candles']) < 200:
                    print(f"  -> Not enough {tf_name} data for {pair}")
                    skip_pair = True
                    break
            
            if skip_pair:
                continue
            
            # Calculate EMAs for all timeframes
            daily_emas = calculate_emas(daily_data)
            weekly_emas = calculate_emas(weekly_data)
            h4_emas = calculate_emas(h4_data)
            h1_emas = calculate_emas(h1_data)
            m15_emas = calculate_emas(m15_data)
            m5_emas = calculate_emas(m5_data)
            
            # Get current price from the most recent daily candle
            if daily_data and 'candles' in daily_data and daily_data['candles']:
                current_price = float(daily_data['candles'][-1]['mid']['c'])
            else:
                print(f"  -> No price data available for {pair}")
                continue
            
            # 1. Check 1hr vs 1d timeframes
            if check_long_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                if check_long_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200']):
                    long_trending_1hr_1d.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to long trending [1hr,1d] list.")
            
            if check_short_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                if check_short_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200']):
                    short_trending_1hr_1d.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to short trending [1hr,1d] list.")
            
            # 2. Check 4hr vs weekly timeframes
            if check_long_trend(current_price, weekly_emas['ema_8'], weekly_emas['ema_50'], weekly_emas['ema_200']):
                if check_long_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200']):
                    long_trending_4hr_weekly.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to long trending [4hr,weekly] list.")
            
            if check_short_trend(current_price, weekly_emas['ema_8'], weekly_emas['ema_50'], weekly_emas['ema_200']):
                if check_short_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200']):
                    short_trending_4hr_weekly.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to short trending [4hr,weekly] list.")
            
            # 3. Check 5min vs 1hr timeframes
            if check_long_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200']):
                if check_long_trend(current_price, m5_emas['ema_8'], m5_emas['ema_50'], m5_emas['ema_200']):
                    long_trending_5min_1hr.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to long trending [5min,1hr] list.")
            
            if check_short_trend(current_price, h1_emas['ema_8'], h1_emas['ema_50'], h1_emas['ema_200']):
                if check_short_trend(current_price, m5_emas['ema_8'], m5_emas['ema_50'], m5_emas['ema_200']):
                    short_trending_5min_1hr.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to short trending [5min,1hr] list.")
            
            # 4. Check 15min vs 4hr timeframes
            if check_long_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200']):
                if check_long_trend(current_price, m15_emas['ema_8'], m15_emas['ema_50'], m15_emas['ema_200']):
                    long_trending_15min_4hr.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to long trending [15min,4hr] list.")
            
            if check_short_trend(current_price, h4_emas['ema_8'], h4_emas['ema_50'], h4_emas['ema_200']):
                if check_short_trend(current_price, m15_emas['ema_8'], m15_emas['ema_50'], m15_emas['ema_200']):
                    short_trending_15min_4hr.append({"pair": pair, "date": run_date})
                    print(f"  -> Added to short trending [15min,4hr] list.")

        except Exception as e:
            print(f"An error occurred for {pair}: {e}")

    # Print all results
    print("\n" + "="*60)
    print("                    FOREX TREND ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nLong Trending Markets [1hr,1d] ({len(long_trending_1hr_1d)} pairs):")
    for item in long_trending_1hr_1d:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nShort Trending Markets [1hr,1d] ({len(short_trending_1hr_1d)} pairs):")
    for item in short_trending_1hr_1d:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nLong Trending Markets [4hr,weekly] ({len(long_trending_4hr_weekly)} pairs):")
    for item in long_trending_4hr_weekly:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nShort Trending Markets [4hr,weekly] ({len(short_trending_4hr_weekly)} pairs):")
    for item in short_trending_4hr_weekly:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nLong Trending Markets [5min,1hr] ({len(long_trending_5min_1hr)} pairs):")
    for item in long_trending_5min_1hr:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nShort Trending Markets [5min,1hr] ({len(short_trending_5min_1hr)} pairs):")
    for item in short_trending_5min_1hr:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nLong Trending Markets [15min,4hr] ({len(long_trending_15min_4hr)} pairs):")
    for item in long_trending_15min_4hr:
        print(f"  {item['pair']} - {item['date']}")
    
    print(f"\nShort Trending Markets [15min,4hr] ({len(short_trending_15min_4hr)} pairs):")
    for item in short_trending_15min_4hr:
        print(f"  {item['pair']} - {item['date']}")
    
    print("\n" + "="*60)
    
    # Export to Excel
    print("\nExporting results to Excel...")
    filename = export_to_excel(
        long_trending_1hr_1d, short_trending_1hr_1d,
        long_trending_4hr_weekly, short_trending_4hr_weekly,
        long_trending_5min_1hr, short_trending_5min_1hr,
        long_trending_15min_4hr, short_trending_15min_4hr,
        run_date
    )
    print(f"Excel file saved as '{filename}'")
    print("="*60)

if __name__ == "__main__":
    main()
