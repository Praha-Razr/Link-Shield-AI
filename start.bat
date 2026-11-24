@echo off
setlocal enabledelayedexpansion

title LINKSHIELD AI - Cyber Threat Intelligence Platform
color 0B

echo ======================================================================
echo    _     ___ _   _ _  ______  _   _ ___ _____ _     ____      _    ___ 
echo   ^| ^|   ^|_ _^| \ ^| ^| ^|/ / ___^|^| ^| ^| ^|_ _^| ____^| ^|   ^|  _ \    / \  ^|_ _^|
echo   ^| ^|    ^| ^|^|  \^| ^| ' /^ \___ \^| ^|_^| ^|^| ^|^|  _^| ^| ^|   ^| ^| ^| ^|  / _ \  ^| ^| 
echo   ^| ^|___ ^| ^|^| ^|\  ^| . \  ___) ^|  _  ^|^| ^|^| ^|___^| ^|___^| ^|_^| ^| / ___ \ ^| ^| 
echo   ^|_____^|___^|_^| \_^|_^|\_\^|____/^|_^| ^|_^|___^|_____^|_____^|____/ /_/   \_\___^|
echo.
echo           DETECT. EXPLAIN. INVESTIGATE. PROTECT.
echo       Cyber Crime Intelligence ^& Threat Investigation Platform
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python installation
echo [1/4] Verifying Python runtime...
set PYTHON_CMD=
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] Python was not found on your system PATH!
        echo Please install Python 3.10+ from https://www.python.org/
        pause
        exit /b 1
    )
)
echo    Found Python runtime (%PYTHON_CMD%).

:: 2. Check Node.js / NPM installation
echo [2/4] Verifying Node.js / NPM environment...
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm was not found on your system PATH!
    echo Please install Node.js v18 or newer from https://nodejs.org/
    pause
    exit /b 1
)
echo    Found Node.js ^& npm runtime.

:: 3. Setup Python virtual environment and backend packages
echo [3/4] Checking Python Virtual Environment (backend\venv)...
if not exist "backend\venv\Scripts\python.exe" (
    echo    Creating virtual environment at backend\venv...
    %PYTHON_CMD% -m venv backend\venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create Python virtual environment.
        pause
        exit /b 1
    )
    echo    Installing backend dependencies from backend\requirements.txt...
    backend\venv\Scripts\python.exe -m pip install --upgrade pip
    backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
) else (
    echo    Virtual environment already configured.
)

:: 3b. Seed default users
echo    Ensuring default officer and demo users are seeded...
backend\venv\Scripts\python.exe backend\seed_users.py

:: 4. Setup Frontend node_modules
echo [4/4] Checking Frontend dependencies (frontend\node_modules)...
if not exist "frontend\node_modules" (
    echo    Installing frontend packages via npm...
    call npm.cmd --prefix frontend install
) else (
    echo    Frontend packages already installed.
)

:: Launch Services in separate dedicated command windows
echo.
echo ======================================================================
echo    Launching LINKSHIELD AI Multi-Tier System...
echo ======================================================================
echo.

echo - Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "LinkShield Backend (FastAPI :8000)" cmd /k "cd /d "%~dp0backend" && "venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo - Starting Vite React Frontend on http://localhost:5173 ...
start "LinkShield Frontend (Vite :5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Services launched. Waiting 4 seconds for servers to initialize...
ping 127.0.0.1 -n 5 >nul

echo - Opening default web browser to http://localhost:5173 ...
start http://localhost:5173

echo.
echo ======================================================================
echo   LINKSHIELD AI IS READY!
echo.
echo   * Web User Interface: http://localhost:5173
echo   * Backend REST API  : http://127.0.0.1:8000
echo   * Interactive Docs  : http://127.0.0.1:8000/docs
echo   * Cyber Helpline    : 1930
echo.
echo   Leave this launcher or close it anytime.
echo   To stop LinkShield, close the Backend and Frontend command windows.
echo ======================================================================
pause
