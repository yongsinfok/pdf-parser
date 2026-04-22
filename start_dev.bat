@echo off
start cmd /k "cd /d "%~dp0backend" && python main.py"
start cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo Starting Backend and Frontend...
pause
