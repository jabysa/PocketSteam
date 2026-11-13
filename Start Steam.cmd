@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python 3.9+ is required. Download: https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )
    python pocketsteam.py
) else (
    py -3 pocketsteam.py
)
if errorlevel 1 pause
