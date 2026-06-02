@echo off

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

pip install -r requirements.txt -q
if errorlevel 1 (
    echo Failed to install Python dependencies!
    pause
    exit /b 1
)
cd web
if not exist node_modules (
    call npm install
    if errorlevel 1 (
        echo Failed to install Node.js dependencies!
        pause
        exit /b 1
    )
)
cd ..

start /b python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
cd web
start /b npm run dev
cd ..
timeout /t 2 /nobreak >nul
start http://localhost:5173

:loop
timeout /t 60 /nobreak >nul
goto loop
