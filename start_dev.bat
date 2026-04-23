@echo off
echo Updating backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt
cd /d "%~dp0"

echo Starting Backend and Frontend...
start "Backend" cmd /k "cd /d "%~dp0backend" && python main.py"
start "Frontend" cmd /k "cd /d "%~dp0frontend" && call npm run dev"
pause
