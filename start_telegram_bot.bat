@echo off
REM RAGMind Telegram Bot Startup Script

echo ========================================
echo    RAGMind Telegram Bot
echo ========================================
echo.
echo [DEBUG] Script started at %DATE% %TIME%
echo [DEBUG] Current directory: "%CD%"
echo [DEBUG] User: %USERNAME%
echo.
REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please run setup.bat to create the configuration file.
    pause
    exit /b 1
)

REM Activate virtual environment
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run start_backend.bat first to create it.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo.

REM Check if bot token is configured
echo Checking configuration...
python -c "from backend.config import settings; assert settings.telegram_bot_token, 'TELEGRAM_BOT_TOKEN not set in .env'" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Telegram bot token not configured!
    echo Please set TELEGRAM_BOT_TOKEN in the .env file
    echo Get token from @BotFather on Telegram
    echo.
    pause
    exit /b 1
)
echo [✓] Bot token configured
echo.

REM Start bot
echo Starting Telegram bot...
echo.
echo [DEBUG] Starting Telegram bot...
echo [DEBUG] Command: python -m telegram_bot.bot
python -m telegram_bot.bot
