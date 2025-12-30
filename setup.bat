@echo off
setlocal EnableExtensions EnableDelayedExpansion

chcp 65001 >nul
color 0A
title RAGMind - Setup

:: Ensure we run from the script directory (project root)
set "ROOT=%~dp0"
pushd "%ROOT%" >nul

echo ========================================
echo    RAGMind - Setup Script
echo    Installing all project requirements
echo ========================================
echo.
echo [DEBUG] Script started at %DATE% %TIME%
echo [INFO] Project root: "%CD%"
echo [DEBUG] Current user: %USERNAME%
echo [DEBUG] Windows version: %OS%
echo.

:: Check if Python is installed
echo [DEBUG] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed on this system!
    echo Please install Python 3.8 or later from: https://www.python.org/
    echo [DEBUG] Python check failed with errorlevel %errorlevel%
    pause
    popd
    exit /b 1
)

echo [✓] Python installed:
python --version
echo [DEBUG] Python check passed
echo.

:: Optional: Check if psql exists (non-blocking)
echo [DEBUG] Checking PostgreSQL client installation...
where psql >nul 2>&1
if errorlevel 1 (
    echo [WARNING] psql not found in PATH. Make sure PostgreSQL is installed and running.
    echo          Download from: https://www.postgresql.org/download/
    echo [DEBUG] psql check returned errorlevel %errorlevel%
) else (
    echo [✓] PostgreSQL client (psql) found
    echo [DEBUG] psql check passed
)
echo.

:: Create virtual environment
echo ========================================
echo 1. Creating Virtual Environment
echo ========================================
echo [DEBUG] Checking for existing virtual environment...
if exist "venv\" (
    echo [WARNING] Virtual environment already exists: "%CD%\venv"
    echo [DEBUG] Virtual environment directory found
    choice /C YN /M "Do you want to recreate it?"
    if errorlevel 2 (
        echo [INFO] Skipping virtual environment creation
        goto skip_venv
    )
    echo [INFO] Deleting existing virtual environment...
    rmdir /s /q "venv"
    if errorlevel 1 (
        echo [ERROR] Failed to delete existing virtual environment!
        echo [DEBUG] rmdir failed with errorlevel %errorlevel%
        pause
        popd
        exit /b 1
    )
    echo [DEBUG] Old virtual environment deleted
)

echo [INFO] Creating new virtual environment...
echo [DEBUG] Running: python -m venv "venv"
python -m venv "venv"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment!
    echo [DEBUG] venv creation failed with errorlevel %errorlevel%
    pause
    popd
    exit /b 1
)
echo [✓] Virtual environment created successfully
echo [DEBUG] Virtual environment created at: "%CD%\venv"
echo.

:skip_venv

:: Activate virtual environment
echo ========================================
echo 2. Activating Virtual Environment
echo ========================================
echo [DEBUG] Checking for activation script...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Activation script not found: venv\Scripts\activate.bat
    echo [DEBUG] Activation script missing - venv may be corrupted
    pause
    popd
    exit /b 1
)
echo [DEBUG] Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    echo [DEBUG] Activation failed with errorlevel %errorlevel%
    pause
    popd
    exit /b 1
)
echo [✓] Virtual environment activated
echo [DEBUG] Python executable now: %VIRTUAL_ENV%\Scripts\python.exe
echo.

:: Upgrade pip and install uv (use python -m pip to guarantee venv pip)
echo ========================================
echo 3. Upgrading pip and installing uv
echo ========================================
echo [DEBUG] Upgrading pip and installing uv...
python -m pip install --upgrade pip uv
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip or install uv
    echo [DEBUG] pip/uv installation failed with errorlevel %errorlevel%
    pause
    popd
    exit /b 1
)
echo [✓] pip upgraded and uv installed
echo [DEBUG] Checking uv version...
uv --version
echo.

:: Resolve requirements file
echo ========================================
echo 4. Installing Required Libraries (may take a few minutes...)
echo ========================================
echo [DEBUG] Looking for requirements file...
set "REQ_FILE="

if exist "backend\requirements.txt" (
    set "REQ_FILE=backend\requirements.txt"
    echo [DEBUG] Found backend\requirements.txt
)
if not defined REQ_FILE if exist "requirements.txt" (
    set "REQ_FILE=requirements.txt"
    echo [DEBUG] Found requirements.txt
)

if not defined REQ_FILE (
    echo [ERROR] Requirements file not found:
    echo        - backend\requirements.txt
    echo        - requirements.txt
    echo.
    echo [INFO] Current directory contents:
    dir /b
    echo.
    if exist "backend\" (
        echo [INFO] Backend directory contents:
        dir /b "backend"
    ) else (
        echo [WARNING] Backend directory does not exist
    )
    echo [DEBUG] Requirements file search failed
    pause
    popd
    exit /b 1
)

echo [INFO] Will install from: "%REQ_FILE%"
echo [DEBUG] Starting package installation with uv...
uv pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo [ERROR] Failed to install libraries!
    echo Check requirements file and internet connection
    echo [DEBUG] uv pip install failed with errorlevel %errorlevel%
    pause
    popd
    exit /b 1
)
echo [✓] All libraries installed successfully
echo [DEBUG] Package installation completed
echo.

:: Create .env file if not exists
echo ========================================
echo 5. Creating Configuration File (.env)
echo ========================================
echo [DEBUG] Checking for existing .env file...
if exist ".env" (
    echo [WARNING] .env file already exists
    echo [DEBUG] .env file found at: "%CD%\.env"
    choice /C YN /M "Do you want to recreate it from template?"
    if errorlevel 2 (
        echo [INFO] Skipping .env creation
        goto skip_env
    )
)

if exist ".env.example" (
    echo [INFO] Copying settings from .env.example...
    echo [DEBUG] Copying .env.example to .env
    copy /Y ".env.example" ".env" >nul
    if errorlevel 1 (
        echo [ERROR] Failed to copy .env.example!
        echo [DEBUG] Copy failed with errorlevel %errorlevel%
        pause
        popd
        exit /b 1
    )
    echo [✓] .env file created
    echo [WARNING] Please edit .env file and add:
    echo     - DATABASE_URL
    echo     - GEMINI_API_KEY
    echo     - TELEGRAM_BOT_TOKEN (optional)
    echo [DEBUG] .env file created successfully
) else (
    echo [WARNING] .env.example file not found
    echo Please create .env file manually with required settings
    echo [DEBUG] .env.example not found
)
echo.

:skip_env

:: Create directories
echo ========================================
echo 6. Creating Project Directories
echo ========================================
echo [DEBUG] Creating uploads directory...
if not exist "uploads\" (
    mkdir "uploads"
    echo [DEBUG] Created uploads directory
) else (
    echo [DEBUG] uploads directory already exists
)
echo [✓] uploads directory ready

echo [DEBUG] Creating qdrant_data directory...
if not exist "qdrant_data\" (
    mkdir "qdrant_data"
    echo [DEBUG] Created qdrant_data directory
) else (
    echo [DEBUG] qdrant_data directory already exists
)
echo [✓] qdrant_data directory ready
echo.

:: Database setup instructions
echo ========================================
echo 7. Database Setup
echo ========================================
echo [WARNING] PostgreSQL must be set up manually:
echo.
echo     1. Start PostgreSQL service
echo     2. Open pgAdmin or psql
echo     3. Run these commands:
echo        CREATE DATABASE ragmind;
echo        \c ragmind
echo        CREATE EXTENSION vector;
echo.
echo     4. Update DATABASE_URL in .env file
echo.
echo [DEBUG] Database setup instructions displayed
choice /C YN /M "Have you set up the database?"
if errorlevel 2 (
    echo [WARNING] Please set up the database before running the project
    echo [DEBUG] User chose not to confirm database setup
) else (
    echo [✓] Database is ready
    echo [DEBUG] User confirmed database setup
)
echo.

:: Initialize database
echo ========================================
echo 8. Initializing Database Tables
echo ========================================
echo [DEBUG] Prompting for database initialization...
choice /C YN /M "Do you want to initialize database tables now?"
if errorlevel 2 goto skip_db_init

echo [INFO] Initializing database...
echo [DEBUG] Running: python -m backend.init_database
python -m backend.init_database
if errorlevel 1 (
    echo [ERROR] Database initialization failed
    echo Please check:
    echo   - PostgreSQL connection
    echo   - DATABASE_URL in .env file
    echo   - pgvector extension installed (CREATE EXTENSION vector;)
    echo [DEBUG] Database init failed with errorlevel %errorlevel%
) else (
    echo [✓] Database initialized successfully
    echo [DEBUG] Database initialization completed
)
goto after_db_init

:skip_db_init
echo [INFO] You can initialize the database later with:
echo     python -m backend.init_database
echo [DEBUG] Database initialization skipped by user

:after_db_init
echo.

:: Summary
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo -----------
echo 1. Edit .env file and add:
echo    - DATABASE_URL (required)
echo    - GEMINI_API_KEY (required)
echo    - TELEGRAM_BOT_TOKEN (optional)
echo.
echo 2. To run the project:
echo    - Start Backend: start_backend.bat
echo    - Start Telegram Bot: start_telegram_bot.bat (optional)
echo.
echo 3. Open browser at: http://localhost:8000
echo.
echo ========================================
echo 📚 For more information, see README.md
echo ========================================
echo.
echo [DEBUG] Setup script completed at %DATE% %TIME%
echo [DEBUG] Exit code: 0
pause

popd >nul
pause
endlocal
