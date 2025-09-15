@echo off
echo Building Forex Trend Screener executable...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build the main executable (fixed version)
echo Building main executable with all timeframes...
pyinstaller --onefile --name "ForexTrendScreener_Main" --icon=none --distpath=./dist --workpath=./build forex_trend_screener_fixed.py

REM Build the lightweight executable
echo Building lightweight executable...
pyinstaller --onefile --name "ForexTrendScreener_Lite" --icon=none --distpath=./dist --workpath=./build forex_trend_screener_lightweight.py

echo.
echo Build complete! 
echo Main executable: ForexTrendScreener_Main.exe (All 28 pairs, 4 timeframe combinations)
echo Lite executable: ForexTrendScreener_Lite.exe (5 pairs, 1 timeframe combination)
echo Both executables can be found in the 'dist' folder.
echo.
pause
