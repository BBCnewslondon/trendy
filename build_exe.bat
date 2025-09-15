@echo off
echo Building all trend screener executables...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build the main forex executable (fixed version)
echo Building main forex executable with all timeframes...
pyinstaller --onefile --name "ForexTrendScreener_Main" --distpath=./dist --workpath=./build forex_trend_screener_fixed.py

REM Build the lightweight forex executable
echo Building lightweight forex executable...
pyinstaller --onefile --name "ForexTrendScreener_Lite" --distpath=./dist --workpath=./build forex_trend_screener_lightweight.py

REM Build commodity trend screener
echo Building commodity trend screener...
pyinstaller --onefile --name "CommodityTrendScreener" --distpath=./dist --workpath=./build commodity_trend_screener.py

REM Build indices trend screener
echo Building indices trend screener...
pyinstaller --onefile --name "IndicesTrendScreener" --distpath=./dist --workpath=./build indices_trend_screener.py

echo.
echo Build complete! 
echo Forex (Main): ForexTrendScreener_Main.exe (All 28 pairs, 4 timeframe combinations)
echo Forex (Lite): ForexTrendScreener_Lite.exe (5 pairs, 1 timeframe combination)
echo Commodities: CommodityTrendScreener.exe (11 commodities, 4 timeframe combinations)
echo Indices: IndicesTrendScreener.exe (5 indices, 4 timeframe combinations)
echo All executables can be found in the 'dist' folder.
echo.
pause
