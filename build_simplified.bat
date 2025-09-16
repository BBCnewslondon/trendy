@echo off
echo Building simplified versions of all trend screeners...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Create executables directory if it doesn't exist
if not exist "executables\simplified" mkdir "executables\simplified"

echo Building Forex Trend Screener (Simple)...
pyinstaller --onefile --distpath "executables\simplified" --name "forex_trend_screener_simple" src\forex_trend_screener_simple.py
if %errorlevel% neq 0 (
    echo Failed to build forex_trend_screener_simple.exe
    pause
    exit /b 1
)

echo.
echo Building Commodity Trend Screener (Simple)...
pyinstaller --onefile --distpath "executables\simplified" --name "commodity_trend_screener_simple" src\commodity_trend_screener_simple.py
if %errorlevel% neq 0 (
    echo Failed to build commodity_trend_screener_simple.exe
    pause
    exit /b 1
)

echo.
echo Building Indices Trend Screener (Simple)...
pyinstaller --onefile --distpath "executables\simplified" --name "indices_trend_screener_simple" src\indices_trend_screener_simple.py
if %errorlevel% neq 0 (
    echo Failed to build indices_trend_screener_simple.exe
    pause
    exit /b 1
)

echo.
echo Building Combined Trend Screener (Simple)...
pyinstaller --onefile --distpath "executables\simplified" --name "combined_trend_screener_simple" src\combined_trend_screener_simple.py
if %errorlevel% neq 0 (
    echo Failed to build combined_trend_screener_simple.exe
    pause
    exit /b 1
)

echo.
echo === BUILD SUMMARY ===
echo All simplified executables built successfully!
echo Location: executables\simplified\
echo.
echo Files created:
echo - forex_trend_screener_simple.exe (Forex: 1hr vs 1d, 4hr vs weekly)
echo - commodity_trend_screener_simple.exe (Commodities: 4hr vs weekly only)
echo - indices_trend_screener_simple.exe (Indices: 4hr vs weekly only)
echo - combined_trend_screener_simple.exe (ALL MARKETS: 1hr vs 1d, includes German 40)
echo.
echo Note: These simplified versions analyze fewer timeframe combinations
echo for faster execution while maintaining accuracy.

REM Clean up build artifacts
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

echo.
echo Build complete!
pause
