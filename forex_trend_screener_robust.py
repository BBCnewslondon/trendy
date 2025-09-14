import sys
import os
import logging
from datetime import datetime

# Set up logging to see what's happening
log_filename = f"forex_screener_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("Starting Forex Trend Screener...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Executable path: {sys.executable}")
    
    # Try importing packages one by one to identify issues
    logger.info("Importing oandapyV20...")
    import oandapyV20
    import oandapyV20.endpoints.instruments as instruments
    
    logger.info("Importing pandas...")
    import pandas as pd
    
    logger.info("All imports successful!")
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error during imports: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# OANDA API credentials
access_token = "89c68ff389fa5e86dd30e8aff7c8935a-b0cb097b4475427f7be111d81e76c94b"
accountID = "101-004-31569953-001"

try:
    api = oandapyV20.API(access_token=access_token, environment="practice")
    logger.info("API connection initialized successfully")
except Exception as e:
    logger.error(f"API initialization error: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# List of forex pairs to check (reduced for testing)
forex_pairs = [
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"
]

def get_historical_data(instrument, granularity, count):
    """Fetches historical data for a given instrument."""
    try:
        params = {
            "count": count,
            "granularity": granularity
        }
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        api.request(r)
        return r.response
    except Exception as e:
        logger.error(f"Error fetching data for {instrument}: {e}")
        return None

def calculate_emas(data):
    """Calculates 8, 50, and 200 EMAs."""
    try:
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
    except Exception as e:
        logger.error(f"Error calculating EMAs: {e}")
        return None

def check_long_trend(price, ema_8, ema_50, ema_200):
    """Checks for a long trend condition."""
    return ema_8 > ema_50 > ema_200 and price > ema_8

def check_short_trend(price, ema_8, ema_50, ema_200):
    """Checks for a short trend condition."""
    return ema_200 > ema_50 > ema_8 and price < ema_8

def export_to_excel(long_1hr_1d, short_1hr_1d, run_date):
    """Export trending markets to an Excel file."""
    try:
        # Create a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"forex_trend_analysis_{timestamp}.xlsx"
        
        # Create DataFrames
        long_df = pd.DataFrame(long_1hr_1d)
        short_df = pd.DataFrame(short_1hr_1d)
        
        # Create Excel writer object
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = [
                {'Category': 'Long Trending [1hr,1d]', 'Count': len(long_df), 'Pairs': ', '.join(long_df['pair'].tolist()) if not long_df.empty else 'None'},
                {'Category': 'Short Trending [1hr,1d]', 'Count': len(short_df), 'Pairs': ', '.join(short_df['pair'].tolist()) if not short_df.empty else 'None'}
            ]
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Individual sheets
            if not long_df.empty:
                long_df.to_excel(writer, sheet_name='Long Trending', index=False)
            else:
                empty_df = pd.DataFrame(columns=['pair', 'date'])
                empty_df.to_excel(writer, sheet_name='Long Trending', index=False)
                
            if not short_df.empty:
                short_df.to_excel(writer, sheet_name='Short Trending', index=False)
            else:
                empty_df = pd.DataFrame(columns=['pair', 'date'])
                empty_df.to_excel(writer, sheet_name='Short Trending', index=False)
        
        logger.info(f"Excel file created: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error creating Excel file: {e}")
        return None

def main():
    """Main function to run the forex trend screener."""
    try:
        logger.info("Starting main analysis...")
        
        long_trending_1hr_1d = []
        short_trending_1hr_1d = []
        run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for pair in forex_pairs:
            logger.info(f"Analyzing {pair}...")
            print(f"Analyzing {pair}...")
            
            try:
                # Get daily data
                daily_data = get_historical_data(pair, "D", 300)
                if not daily_data or 'candles' not in daily_data or len(daily_data['candles']) < 200:
                    logger.warning(f"Not enough daily data for {pair}")
                    continue
                
                # Get hourly data
                hourly_data = get_historical_data(pair, "H1", 300)
                if not hourly_data or 'candles' not in hourly_data or len(hourly_data['candles']) < 200:
                    logger.warning(f"Not enough hourly data for {pair}")
                    continue
                
                # Calculate EMAs
                daily_emas = calculate_emas(daily_data)
                hourly_emas = calculate_emas(hourly_data)
                
                if daily_emas is None or hourly_emas is None:
                    logger.warning(f"Failed to calculate EMAs for {pair}")
                    continue
                
                current_price = float(daily_data['candles'][-1]['mid']['c'])
                
                # Check for long trend
                if check_long_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                    if check_long_trend(current_price, hourly_emas['ema_8'], hourly_emas['ema_50'], hourly_emas['ema_200']):
                        long_trending_1hr_1d.append({"pair": pair, "date": run_date})
                        logger.info(f"Added {pair} to long trending list")
                        print(f"  -> Added to long trending list.")

                # Check for short trend
                if check_short_trend(current_price, daily_emas['ema_8'], daily_emas['ema_50'], daily_emas['ema_200']):
                    if check_short_trend(current_price, hourly_emas['ema_8'], hourly_emas['ema_50'], hourly_emas['ema_200']):
                        short_trending_1hr_1d.append({"pair": pair, "date": run_date})
                        logger.info(f"Added {pair} to short trending list")
                        print(f"  -> Added to short trending list.")

            except Exception as e:
                logger.error(f"Error analyzing {pair}: {e}")
                continue

        # Print results
        print("\n" + "="*60)
        print("                    FOREX TREND ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nLong Trending Markets [1hr,1d] ({len(long_trending_1hr_1d)} pairs):")
        for item in long_trending_1hr_1d:
            print(f"  {item['pair']} - {item['date']}")
        
        print(f"\nShort Trending Markets [1hr,1d] ({len(short_trending_1hr_1d)} pairs):")
        for item in short_trending_1hr_1d:
            print(f"  {item['pair']} - {item['date']}")
        
        print("\n" + "="*60)
        
        # Export to Excel
        print("\nExporting results to Excel...")
        logger.info("Starting Excel export...")
        filename = export_to_excel(long_trending_1hr_1d, short_trending_1hr_1d, run_date)
        
        if filename:
            print(f"Excel file saved as '{filename}'")
            logger.info(f"Excel export successful: {filename}")
        else:
            print("Failed to create Excel file")
            logger.error("Excel export failed")
        
        print("="*60)
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Main function error: {e}")
        print(f"An error occurred: {e}")
    
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
