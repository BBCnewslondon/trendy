@echo off
echo Building all trend screener executables...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Create executables directory if it doesn't exist
if not exist "executables" mkdir executables

REM Build the main forex executable (fixed version)
echo Building main forex executable with all timeframes...
pyinstaller --onefile --name "ForexTrendScreener_Fixed" --distpath=./executables --workpath=./temp_build src/forex_trend_screener_fixed.py

REM Build the lightweight forex executable
echo Building lightweight forex executable...
pyinstaller --onefile --name "ForexTrendScreener_Lite" --distpath=./executables --workpath=./temp_build src/forex_trend_screener_lightweight.py

REM Build commodity trend screener
echo Building commodity trend screener...
pyinstaller --onefile --name "CommodityTrendScreener_Fixed" --distpath=./executables --workpath=./temp_build src/commodity_trend_screener.py

REM Build indices trend screener
echo Building indices trend screener...
pyinstaller --onefile --name "IndicesTrendScreener_Fixed" --distpath=./executables --workpath=./temp_build src/indices_trend_screener.py

REM Clean up temporary build files
echo Cleaning up temporary files...
if exist "temp_build" rmdir /s /q temp_build
if exist "*.spec" del /q *.spec

echo.
echo Build complete! 
echo Forex (Main): ForexTrendScreener_Fixed.exe (All 28 pairs, 4 timeframe combinations)
echo Forex (Lite): ForexTrendScreener_Lite.exe (5 pairs, 1 timeframe combination)
echo Commodities: CommodityTrendScreener_Fixed.exe (11 commodities, 4 timeframe combinations)
echo Indices: IndicesTrendScreener_Fixed.exe (5 indices, 4 timeframe combinations)
echo All executables can be found in the 'executables' folder.
echo.
pause
