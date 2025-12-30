@echo off
chcp 65001 >nul
color 0E
echo ========================================
echo    RAGMind - Update GitHub
echo    Update project on GitHub
echo ========================================
echo.
echo [DEBUG] Script started at %DATE% %TIME%
echo [DEBUG] Current directory: "%CD%"

:: Check if Git is initialized
if not exist ".git\" (
    echo [ERROR] Project is not connected to Git!
    echo Please run push_to_github.bat first
    echo [DEBUG] .git directory not found
    pause
    exit /b 1
)
echo [DEBUG] Git repository found
echo.

echo ========================================
echo 1. Adding New Changes
echo ========================================
echo [DEBUG] Running: git add .
git add .
echo [✓] Changes added
echo [DEBUG] Files staged
echo.

echo ========================================
echo 2. Showing Changed Files
echo ========================================
echo [DEBUG] Running: git status --short
git status --short
echo [DEBUG] Status displayed
echo.

echo ========================================
echo 3. Creating Commit
echo ========================================
set /p COMMIT_MSG="Enter description of changes: "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update project files
echo [DEBUG] Commit message: "%COMMIT_MSG%"

echo [DEBUG] Running: git commit -m "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo [WARNING] No new changes to commit
    echo [DEBUG] git commit returned errorlevel %errorlevel%
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if errorlevel 2 (
        echo [INFO] Cancelled
        echo [DEBUG] User cancelled operation
        pause
        exit /b 0
    )
)
echo [✓] Commit created
echo [DEBUG] Commit operation completed
echo.

echo ========================================
echo 4. Pushing Updates to GitHub
echo ========================================
echo [INFO] Pushing updates...
echo [DEBUG] Running: git push
git push
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to push updates!
    echo.
    echo Try the following command:
    echo   git pull origin main --rebase
    echo   git push
    echo.
    echo [DEBUG] Push failed with errorlevel %errorlevel%
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Project updated successfully!
echo ========================================
echo.
echo [DEBUG] Update completed at %DATE% %TIME%
pause
