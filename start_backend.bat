@echo off
REM RAGMind Backend Startup Script

echo ========================================
echo    RAGMind Backend Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing/Updating dependencies...
pip install -r backend\requirements.txt
echo.

REM Initialize database
echo Initializing database...
python backend\init_database.py
echo.

REM Start server
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
