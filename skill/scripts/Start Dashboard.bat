@echo off
REM Double-click to start (or re-open) the live Second Brain dashboard.
REM Serves the vault this file sits in; close this window to stop it.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 dashboard_server.py --open
) else (
  python dashboard_server.py --open
)
echo.
echo Dashboard stopped.
pause
