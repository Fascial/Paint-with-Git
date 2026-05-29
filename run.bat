@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    where uv >nul 2>nul
    if %errorlevel% neq 0 (
        echo Installing uv...
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        set "PATH=%LOCALAPPDATA%\uv\bin;%PATH%"
    )
    echo Setting up environment for the first time...
    uv sync
    if %errorlevel% neq 0 (
        echo Error: Failed to sync dependencies.
        pause
        exit /b %errorlevel%
    )
)

start "" ".venv\Scripts\pythonw.exe" -m src.ui