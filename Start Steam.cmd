@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python steam_portable.py
) else (
    py -3 steam_portable.py
)
if errorlevel 1 pause
