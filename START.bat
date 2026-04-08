@echo off
title Indian Stock Intelligence Studio
cls

echo.
echo  ================================================================
echo  ^|                                                              ^|
echo  ^|         INDIAN STOCK INTELLIGENCE STUDIO                    ^|
echo  ^|            Powered by 10-Agent AI System                    ^|
echo  ^|                                                              ^|
echo  ================================================================
echo.

REM ----------------------------------------------------------------
REM Check setup was completed
REM ----------------------------------------------------------------
if not exist .venv\Scripts\python.exe (
    echo  ERROR: Setup has not been completed yet.
    echo.
    echo  Please double-click  SETUP.bat  first to install everything.
    echo.
    pause
    exit /b 1
)

if not exist .env (
    echo  ERROR: Configuration file (.env) is missing.
    echo.
    echo  Please double-click  SETUP.bat  and follow the steps.
    echo.
    pause
    exit /b 1
)

REM ----------------------------------------------------------------
REM Start the server and open the browser
REM ----------------------------------------------------------------
echo  Starting the AI server...
echo.
echo  Your browser will open automatically in a few seconds.
echo.
echo  ----------------------------------------------------------------
echo   App URL  :  http://127.0.0.1:8000
echo  ----------------------------------------------------------------
echo   Login with the admin account:
echo     Username :  admin
echo     Password :  admin123
echo.
echo   Or click Register on the login page to create your own account.
echo  ----------------------------------------------------------------
echo.
echo  To STOP the server: close this window or press Ctrl+C
echo.
echo  ================================================================
echo.

REM Open browser after a short delay (gives server time to start)
powershell -NoLogo -NonInteractive -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"

REM Launch the web server (this keeps the window open)
.venv\Scripts\python web_server.py

echo.
echo  Server stopped. Press any key to close...
pause >nul

