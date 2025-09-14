import pandas as pd
from datetime import datetime

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

# Test data
run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
test_long_1hr_1d = [{"pair": "EUR_USD", "date": run_date}, {"pair": "GBP_USD", "date": run_date}]
test_short_1hr_1d = [{"pair": "USD_JPY", "date": run_date}]
test_long_4hr_weekly = [{"pair": "AUD_USD", "date": run_date}]
test_short_4hr_weekly = []
test_long_5min_1hr = [{"pair": "EUR_JPY", "date": run_date}]
test_short_5min_1hr = []
test_long_15min_4hr = []
test_short_15min_4hr = []

print("Testing Excel export functionality...")
filename = export_to_excel(
    test_long_1hr_1d, test_short_1hr_1d,
    test_long_4hr_weekly, test_short_4hr_weekly,
    test_long_5min_1hr, test_short_5min_1hr,
    test_long_15min_4hr, test_short_15min_4hr,
    run_date
)
print(f"Test Excel file created: {filename}")
