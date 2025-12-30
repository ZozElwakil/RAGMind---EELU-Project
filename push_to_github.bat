@echo off
chcp 65001 >nul
color 0B
echo ========================================
echo    RAGMind - Push to GitHub
echo    Push project to GitHub
echo ========================================
echo.
echo [DEBUG] Script started at %DATE% %TIME%
echo [DEBUG] Current directory: "%CD%"

:: Repository URL - CHANGE THIS!
set REPO_URL=https://github.com/ZozElwakil/RAGMind.git

echo [WARNING] IMPORTANT: Make sure to change REPO_URL in this file!
echo     Current URL: %REPO_URL%
echo.
choice /C YN /M "Have you changed the URL to your own repository?"
if errorlevel 2 (
    echo [WARNING] Please edit the file and change REPO_URL
    echo [DEBUG] User chose not to confirm repository URL
    pause
    exit /b 1
)
echo [DEBUG] Repository URL confirmed
echo.

echo ========================================
echo 1. Initialize Git Repository
echo ========================================
echo [DEBUG] Checking for existing Git repository...

:: Check if already initialized
if exist ".git\" (
    echo [✓] Git repository already exists
    echo [DEBUG] .git directory found
) else (
    echo [INFO] Initializing Git...
    echo [DEBUG] Running: git init
    git init
    if errorlevel 1 (
        echo [ERROR] Failed to initialize Git!
        echo Make sure Git is installed: https://git-scm.com/
        echo [DEBUG] git init failed with errorlevel %errorlevel%
        pause
        exit /b 1
    )
    echo [✓] Git initialized successfully
    echo [DEBUG] Git repository created
)
echo.

echo ========================================
echo 2. Adding All Files
echo ========================================
echo [DEBUG] Running: git add .
git add .
if errorlevel 1 (
    echo [ERROR] Failed to add files!
    echo [DEBUG] git add failed with errorlevel %errorlevel%
    pause
    exit /b 1
)
echo [✓] All files added
echo [DEBUG] Files staged for commit
echo.

echo ========================================
echo 3. Creating Commit
echo ========================================
echo [DEBUG] Running: git commit -m "Initial commit: RAGMind - Intelligent Document Q&A System"
git commit -m "Initial commit: RAGMind - Intelligent Document Q&A System"
if errorlevel 1 (
    echo [WARNING] No new changes or commit already exists
    echo [DEBUG] git commit returned errorlevel %errorlevel%
)
echo [✓] Commit created
echo [DEBUG] Commit operation completed
echo.

echo ========================================
echo 4. Naming Main Branch
echo ========================================
echo [DEBUG] Running: git branch -M main
git branch -M main
if errorlevel 1 (
    echo [WARNING] Failed to rename branch
    echo [DEBUG] git branch failed with errorlevel %errorlevel%
) else (
    echo [✓] Branch renamed to main
    echo [DEBUG] Branch renamed successfully
)
echo.

echo ========================================
echo 5. Connecting Project to GitHub
echo ========================================
echo [DEBUG] Checking for existing origin remote...

:: Check if origin already exists
git remote | findstr /C:"origin" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Connecting project to %REPO_URL%...
    echo [DEBUG] Running: git remote add origin %REPO_URL%
    git remote add origin %REPO_URL%
    if errorlevel 1 (
        echo [ERROR] Failed to connect project!
        echo [DEBUG] git remote add failed with errorlevel %errorlevel%
        pause
        exit /b 1
    )
    echo [✓] Project connected successfully
    echo [DEBUG] Remote origin added
) else (
    echo [WARNING] Remote origin already exists
    echo [INFO] Updating URL...
    echo [DEBUG] Running: git remote set-url origin %REPO_URL%
    git remote set-url origin %REPO_URL%
    echo [✓] URL updated
    echo [DEBUG] Remote origin URL updated
)
echo.

echo ========================================
echo 6. Pushing Files to GitHub
echo ========================================
echo [INFO] Pushing files...
echo [WARNING] You will be prompted for:
echo     - Username: Your GitHub username
echo     - Password: Personal Access Token (NOT your regular password!)
echo.
echo [INFO] To get a Token:
echo     GitHub → Settings → Developer settings → Personal access tokens
echo.
echo [DEBUG] Running: git push -u origin main
git push -u origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to push files!
    echo.
    echo Possible causes:
    echo   1. Incorrect credentials (use Token, not Password)
    echo   2. Incorrect URL
    echo   3. No internet connection
    echo.
    echo To try again, run the command:
    echo   git push -u origin main
    echo.
    echo [DEBUG] Push failed with errorlevel %errorlevel%
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Project pushed successfully!
echo ========================================
echo.
echo You can now visit the project at:
echo %REPO_URL%
echo.
echo For future updates, use: update_github.bat
echo.
echo [DEBUG] Push completed successfully at %DATE% %TIME%
pause
