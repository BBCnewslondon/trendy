# Trend Analysis Suite for OANDA Markets

This repository contains a comprehensive suite of trend analysis applications that analyze forex pairs, commodities, and stock indices using the OANDA API. All programs use the same EMA-based trend detection algorithm with multiple timeframe analysis.

## Project Structure

```
trendy/
├── src/                           # Source code files
│   ├── forex_trend_screener_fixed.py     # Main forex screener (28 pairs, 4 timeframes)
│   ├── forex_trend_screener_lightweight.py  # Quick forex screener (5 pairs)
│   ├── forex_trend_screener_simple.py    # Simplified forex (28 pairs, 2 timeframes)
│   ├── commodity_trend_screener.py       # Full commodity screener (11 commodities, 4 timeframes)
│   ├── commodity_trend_screener_simple.py # Simple commodity (11 commodities, 1 timeframe)
│   ├── indices_trend_screener.py         # Full indices screener (5 indices, 4 timeframes)
│   └── indices_trend_screener_simple.py  # Simple indices (5 indices, 1 timeframe)
├── executables/                   # Ready-to-use executables
│   ├── ForexTrendScreener_Fixed.exe      # Main forex screener
│   ├── ForexTrendScreener_Lite.exe       # Lightweight forex screener
│   ├── CommodityTrendScreener_Fixed.exe  # Full commodity screener
│   ├── IndicesTrendScreener_Fixed.exe    # Full stock index screener
│   └── simplified/               # Faster simplified versions
│       ├── forex_trend_screener_simple.exe      # Forex (2 timeframes only)
│       ├── commodity_trend_screener_simple.exe  # Commodity (1 timeframe only)
│       └── indices_trend_screener_simple.exe    # Indices (1 timeframe only)
├── sample_output/                 # Sample CSV output files
├── build_exe.bat                  # Build script for full versions
├── build_simplified.bat           # Build script for simplified versions
├── requirements.txt               # Python dependencies
├── SIMPLIFIED_VERSIONS.md         # Documentation for simplified versions
└── README.md                      # This file
```

## Programs Included

### 1. Forex Trend Screener
**Full Version:** `src/forex_trend_screener_fixed.py`, `executables/ForexTrendScreener_Fixed.exe`
**Simple Version:** `src/forex_trend_screener_simple.py`, `executables/simplified/forex_trend_screener_simple.exe`

- Analyzes **28 major and minor forex pairs**
- Covers all major currencies: EUR, GBP, USD, JPY, CHF, CAD, AUD, NZD
- **Full version:** 4 timeframe combinations analyzed per pair
- **Simple version:** 2 timeframe combinations (1hr vs 1d, 4hr vs weekly) - ~50% faster
- Generates detailed CSV reports

### 2. Commodity Trend Screener
**Full Version:** `src/commodity_trend_screener.py`, `executables/CommodityTrendScreener_Fixed.exe`
**Simple Version:** `src/commodity_trend_screener_simple.py`, `executables/simplified/commodity_trend_screener_simple.exe`

- Analyzes **11 major commodities**:
  - **Precious Metals:** Gold (XAU_USD), Silver (XAG_USD), Platinum (XPT_USD), Palladium (XPD_USD)
  - **Energy:** West Texas Oil (WTICO_USD), Brent Crude Oil (BCO_USD), Natural Gas (NATGAS_USD)
  - **Agricultural:** Corn (CORN_USD), Soybeans (SOYBN_USD), Wheat (WHEAT_USD), Sugar (SUGAR_USD)
- **Full version:** 4 timeframe combinations analyzed per commodity
- **Simple version:** 1 timeframe combination (4hr vs weekly) - ~75% faster
- Generates detailed CSV reports

### 3. Stock Index Trend Screener
**Full Version:** `src/indices_trend_screener.py`, `executables/IndicesTrendScreener_Fixed.exe`
**Simple Version:** `src/indices_trend_screener_simple.py`, `executables/simplified/indices_trend_screener_simple.exe`

- Analyzes **5 major stock indices**:
  - **US Indices:** S&P 500 (SPX500_USD), NASDAQ 100 (NAS100_USD), Dow Jones 30 (US30_USD)
  - **International:** FTSE 100 (UK100_GBP)
  - **Bonds:** US 10-Year Treasury Note (USB10Y_USD)
- **Full version:** 4 timeframe combinations analyzed per index
- **Simple version:** 1 timeframe combination (4hr vs weekly) - ~75% faster
- Generates detailed CSV reports

### 4. Lightweight Forex Screener
**Files:** `src/forex_trend_screener_lightweight.py`, `executables/ForexTrendScreener_Lite.exe`

- Quick analysis of **5 major forex pairs**
- Single timeframe combination (1hr vs 1d)
- Fast execution for quick market overview

## Trend Detection Algorithm

All programs use the same sophisticated EMA-based trend detection:

### EMAs Calculated
- **EMA 8** (Short-term)
- **EMA 50** (Medium-term) 
- **EMA 200** (Long-term)

### Trend Conditions
- **Long Trend:** Price > EMA_8 > EMA_50 > EMA_200 (on BOTH timeframes)
- **Short Trend:** Price < EMA_8 < EMA_50 < EMA_200 (on BOTH timeframes)

### Timeframe Combinations Analyzed
1. **1hr vs 1d** - Hourly and Daily alignment
2. **4hr vs weekly** - 4-hour and Weekly alignment
3. **5min vs 1hr** - 5-minute and Hourly alignment
4. **15min vs 4hr** - 15-minute and 4-hour alignment

## Output Format

All programs generate CSV files with the following structure:

```csv
Instrument,Price,Timeframe_Combination,Trend_Type,Higher_TF_EMA_8,Higher_TF_EMA_50,Higher_TF_EMA_200,Lower_TF_EMA_8,Lower_TF_EMA_50,Lower_TF_EMA_200,Date
EUR_USD,1.17616,1hr vs 1d,Long,1.17234,1.16442,1.12917,1.17438,1.17287,1.17101,2025-09-15 12:58:31
```

## Requirements

### For Python Scripts
- Python 3.12+
- requests library
- OANDA API access token

### For Executables
- No dependencies required
- Standalone executables ready to run
- Windows 64-bit compatible

## OANDA API Setup

1. Create a free OANDA practice account
2. Get your API access token
3. Update the `access_token` variable in the scripts

## Usage

### Running Python Scripts
```bash
python src/forex_trend_screener_fixed.py
python src/commodity_trend_screener.py
python src/indices_trend_screener.py
python src/forex_trend_screener_lightweight.py
```

### Running Executables

#### Full Versions (Comprehensive Analysis)
```cmd
executables\ForexTrendScreener_Fixed.exe      # All 28 forex pairs, 4 timeframes
executables\CommodityTrendScreener_Fixed.exe  # All 11 commodities, 4 timeframes  
executables\IndicesTrendScreener_Fixed.exe    # All 5 indices, 4 timeframes
executables\ForexTrendScreener_Lite.exe       # 5 major forex pairs only
```

#### Simplified Versions (Faster Execution)
```cmd
executables\simplified\forex_trend_screener_simple.exe      # 28 forex pairs, 2 timeframes (~50% faster)
executables\simplified\commodity_trend_screener_simple.exe  # 11 commodities, 1 timeframe (~75% faster)
executables\simplified\indices_trend_screener_simple.exe    # 5 indices, 1 timeframe (~75% faster)
```

**Note:** Simplified versions display results in terminal only (no CSV files) for instant analysis.

## Choosing Between Full and Simplified Versions

### Use Full Versions When:
- You need comprehensive analysis across all timeframes
- Multiple timeframe confirmation is required
- Research and detailed analysis is the goal
- Time is not a constraint

### Use Simplified Versions When:
- Quick market scanning is needed
- Regular monitoring/alerts
- Faster execution is preferred
- Focus on key timeframe combinations only
- Terminal output is sufficient (no CSV needed)
- Real-time analysis without file management

## Building Executables

### Full Versions
Use the provided build script:
```batch
build_exe.bat
```

### Simplified Versions  
Use the simplified build script:
```batch
build_simplified.bat
```

Or build manually with PyInstaller:
```bash
pyinstaller --onefile --name "ProgramName" --distpath=./executables src/script_name.py
```

## Sample Results

### Forex Analysis (28 pairs × 4 timeframes = up to 112 signals)
- Typically finds 20-40 trending pairs across all timeframes
- Mix of major and minor pairs
- Long and short opportunities identified

### Commodity Analysis (11 commodities × 4 timeframes = up to 44 signals)
- Focus on precious metals, energy, and agricultural products
- Particularly effective for trending commodities like Gold, Silver, Oil
- Typically finds 10-20 trending signals

### Index Analysis (5 indices × 4 timeframes = up to 20 signals)
- Covers major US and international stock indices
- Includes bond index for diversification
- Typically finds 5-10 trending signals

## Features

- **Real-time data** from OANDA API
- **Multiple timeframe analysis** for confirmation
- **CSV export** for further analysis
- **Standalone executables** for easy distribution
- **Detailed logging** with timestamps
- **Error handling** for robust operation
- **Manual EMA calculations** (no pandas dependency in executables)

## Technical Details

- Uses OANDA's practice environment for safe testing
- Fetches 250 candles per timeframe for accurate EMA calculation
- Implements proper null checking and error handling
- Optimized for executable packaging with PyInstaller
- No external dependencies in executables (requests library embedded)

## Market Coverage

- **Forex:** All major and minor pairs (EUR, GBP, USD, JPY, CHF, CAD, AUD, NZD)
- **Commodities:** Precious metals, energy, agricultural products
- **Indices:** US stock indices, international indices, bond indices
- **Total instruments:** 44 unique instruments analyzed

This comprehensive suite provides complete market coverage for trend analysis across multiple asset classes using professional-grade algorithms and real-time data.
