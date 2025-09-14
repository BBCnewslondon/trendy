@echo off
echo Building Forex Trend Screener executable...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Build the executable
pyinstaller --onefile --name "ForexTrendScreener" --icon=none --distpath=./dist --workpath=./build forex_trend_screener.py

echo.
echo Build complete! 
echo The executable can be found in the 'dist' folder.
echo.
pause
