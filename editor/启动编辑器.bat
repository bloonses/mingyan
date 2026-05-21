@echo off
title 鸣言编辑器
color 0A
cls

echo Starting Mingyan Editor...
cd /d "%~dp0"

if not exist "node_modules" (
    echo Installing dependencies...
    npm install > npm_install.log 2>&1
)

echo Starting development server...
start /B npm run dev

timeout /t 2 /nobreak >nul

for /f "tokens=1-5" %%a in ('netstat -ano ^| findstr ":517" ^| findstr "LISTENING"') do (
    set "port=%%b"
    goto :found
)

:found
set "port=%port::=%"
start http://localhost:%port%/

echo Mingyan Editor is running at http://localhost:%port%/
echo Press any key to close this window...
pause >nul
