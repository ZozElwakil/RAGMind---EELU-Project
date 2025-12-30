@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ========================================
REM RAGMind Backend Startup Script
REM ========================================

echo ========================================
echo    RAGMind Backend Server
echo ========================================
echo.
echo [DEBUG] Script started at %DATE% %TIME%
echo [DEBUG] User: %USERNAME%
echo.

REM --- Always run from script directory ---
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%" >nul
echo [DEBUG] Script directory: "%SCRIPT_DIR%"
echo [DEBUG] Current directory: "%CD%"
echo.

REM --- Check if virtual environment exists ---
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the project.
    echo Expected: "%CD%\venv\Scripts\activate.bat"
    pause
    popd
    exit /b 1
)

REM --- Check if .env exists ---
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please run setup.bat to create the configuration file.
    pause
    popd
    exit /b 1
)

REM --- Activate virtual environment ---
echo Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    popd
    exit /b 1
)
echo.

REM --- Quick sanity: show python path/version ---
python -c "import sys; print('[DEBUG] Python:', sys.executable); print('[DEBUG] Version:', sys.version.split()[0])"
echo.

REM --- Check configuration (Gemini key) ---
echo Checking configuration...
python -c "from backend.config import settings; assert settings.gemini_api_key, 'GEMINI_API_KEY not set in .env'" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: GEMINI_API_KEY not configured!
    echo Please set GEMINI_API_KEY in the .env file
    echo Get your key from: https://makersuite.google.com/app/apikey
    echo.
    pause
    popd
    exit /b 1
)
echo [✓] Configuration OK
echo.

REM --- Print DATABASE_URL safely (mask password) ---
echo [DEBUG] Reading DATABASE_URL from backend.config (masked)...
python -c "import re; from backend.config import settings; u=str(getattr(settings,'database_url','')); print('[DEBUG] DATABASE_URL =', re.sub(r':([^:@/]+)@', ':***@', u) if u else '<EMPTY>')"
echo.

REM --- Ensure DATABASE_URL exists and prefer 127.0.0.1 instead of localhost ---
REM (Avoid ipv6 ::1 edge cases and make behavior consistent)
python -c "from backend.config import settings; assert getattr(settings,'database_url',None), 'DATABASE_URL not set in .env'" 2>nul
if errorlevel 1 (
    echo ERROR: DATABASE_URL not set in .env
    echo Please set DATABASE_URL, e.g.:
    echo   DATABASE_URL=postgresql+asyncpg://postgres:saeed@127.0.0.1:5432/ragmind
    pause
    popd
    exit /b 1
)

REM If .env still has localhost, patch it in-place to 127.0.0.1 (safe, local dev)
findstr /I "DATABASE_URL=.*@localhost:" ".env" >nul
if not errorlevel 1 (
    echo [DEBUG] Detected localhost in .env DATABASE_URL - rewriting to 127.0.0.1 for stability...
    powershell -NoProfile -Command ^
      "$p='.env'; $c=Get-Content $p -Raw; $c=$c -replace '@localhost:', '@127.0.0.1:'; Set-Content -Path $p -Value $c -NoNewline"
    echo [✓] Updated .env: localhost -^> 127.0.0.1
    echo.
)

REM --- Smoke test DB connectivity using asyncpg (fast & reliable) ---
echo Testing database connectivity...
python -c "import asyncio; import asyncpg; from backend.config import settings; async def t(): c=await asyncpg.connect(str(settings.database_url)); v=await c.fetchval('select 1'); await c.close(); print('[✓] DB OK, select 1 ->', v); asyncio.run(t())"
if errorlevel 1 (
    echo.
    echo ERROR: Database connectivity test failed!
    echo - Ensure PostgreSQL is running
    echo - Ensure user/password are correct in .env DATABASE_URL
    echo - Ensure database exists (ragmind)
    echo.
    pause
    popd
    exit /b 1
)
echo.

REM --- Initialize database ---
echo Initializing database...
python backend\init_database.py
if errorlevel 1 (
    echo.
    echo ERROR: Database initialization failed!
    echo Please ensure PostgreSQL is running and configured correctly.
    echo Check DATABASE_URL in .env file
    echo.
    pause
    popd
    exit /b 1
)
echo [✓] Database initialized
echo.

REM --- Start server ---
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo [DEBUG] Starting uvicorn server...
echo [DEBUG] Command: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

popd
endlocal
