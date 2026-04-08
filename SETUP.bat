@echo off
setlocal enabledelayedexpansion
title Indian Stock AI - Setup
cls

echo.
echo  ================================================================
echo  ^|                                                              ^|
echo  ^|       INDIAN STOCK INTELLIGENCE STUDIO                      ^|
echo  ^|              ONE-CLICK SETUP                                 ^|
echo  ^|                                                              ^|
echo  ^|  This will install everything needed to run the app.        ^|
echo  ^|                                                              ^|
echo  ================================================================
echo.
echo  Steps that will run automatically:
echo    [1] Check Python installation
echo    [2] Create isolated Python environment
echo    [3] Install all required packages
echo    [4] Download language processing data
echo    [5] Set up your OpenAI API key
echo    [6] Initialise the database
echo.
echo  Press any key to begin setup...
pause >nul
echo.

REM ================================================================
REM STEP 1 - Check Python
REM ================================================================
echo  [STEP 1/6]  Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  *** ERROR: Python is not installed or not found ***
    echo.
    echo  Please follow these steps:
    echo    1. Open your browser and go to: https://www.python.org/downloads/
    echo    2. Click the big yellow "Download Python" button
    echo    3. Run the installer
    echo    4. IMPORTANT: On the first screen, tick the box that says
    echo       "Add Python to PATH"  ^<-- this step is critical
    echo    5. Click Install Now
    echo    6. After installation finishes, close this window and
    echo       double-click SETUP.bat again
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  OK  Python %PY_VER% detected
echo.

REM ================================================================
REM STEP 2 - Create virtual environment
REM ================================================================
echo  [STEP 2/6]  Creating isolated Python environment...
if exist .venv\Scripts\python.exe (
    echo  OK  Environment already exists, skipping
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo  ERROR: Could not create environment.
        echo  Try right-clicking SETUP.bat and choosing "Run as administrator"
        pause
        exit /b 1
    )
    echo  OK  Environment created in .venv folder
)
echo.

REM ================================================================
REM STEP 3 - Install packages
REM ================================================================
echo  [STEP 3/6]  Installing packages... (3 to 5 minutes, please wait)
echo.
.venv\Scripts\python -m pip install --upgrade pip --quiet --disable-pip-version-check
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Package installation failed.
    echo  Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.
echo  OK  All packages installed successfully
echo.

REM ================================================================
REM STEP 4 - Download language data (NLTK / TextBlob)
REM ================================================================
echo  [STEP 4/6]  Downloading language processing data...
.venv\Scripts\python -c "import nltk; [nltk.download(x, quiet=True) for x in ['punkt','punkt_tab','averaged_perceptron_tagger','averaged_perceptron_tagger_eng','brown','wordnet','stopwords']]"
.venv\Scripts\python -m textblob.download_corpora 2>nul
echo  OK  Language data downloaded
echo.

REM ================================================================
REM STEP 5 - API key and .env setup
REM ================================================================
echo  [STEP 5/6]  Setting up configuration...
echo.
if exist .env (
    echo  OK  Configuration file already exists, skipping
    echo      To reset: delete the .env file and re-run SETUP.bat
) else (
    (
        echo OPENAI_API_KEY=sk-clb-z-lrfCPRvGIlTt_ms6jzF2_mfn8olnH60Yhf6kq9EzA
        echo OPENAI_BASE_URL=https://216.9.224.149/v1
        echo MODEL_NAME=gpt-5.4-mini
        echo EXA_MCP_HTTP_URL=https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa,crawling_exa,company_research_exa,linkedin_search_exa,deep_researcher_start,deep_researcher_check
        echo EXA_HTTP_TIMEOUT_SECONDS=25
        echo EXA_DEEP_RESEARCH_TIMEOUT_SECONDS=120
        echo EXA_DEEP_RESEARCH_POLL_INTERVAL_SECONDS=6
    ) > .env
    echo  OK  Configuration created automatically (API key pre-configured)
)
echo.

REM ================================================================
REM STEP 6 - Initialise database
REM ================================================================
echo  [STEP 6/6]  Setting up the database...
.venv\Scripts\python -c "import sys; sys.path.insert(0,'.'); from web_server import ensure_schema; ensure_schema()"
if %errorlevel% neq 0 (
    echo  ERROR: Database setup failed. Please contact support.
    pause
    exit /b 1
)
echo  OK  Database ready
echo.

REM ================================================================
REM SUCCESS
REM ================================================================
echo.
echo  ================================================================
echo  ^|                                                              ^|
echo  ^|              SETUP COMPLETE!  All done.                     ^|
echo  ^|                                                              ^|
echo  ^|  To START the app anytime:                                  ^|
echo  ^|     Double-click  START.bat                                 ^|
echo  ^|                                                              ^|
echo  ^|  Then your browser will open automatically.                 ^|
echo  ^|                                                              ^|
echo  ^|  Default login credentials:                                 ^|
echo  ^|     Username :  admin                                       ^|
echo  ^|     Password :  admin123                                    ^|
echo  ^|                                                              ^|
echo  ^|  You can also register a new account from the login page.  ^|
echo  ^|                                                              ^|
echo  ================================================================
echo.
echo  Press any key to close this window...
pause >nul
endlocal

