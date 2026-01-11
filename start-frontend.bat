@echo off
REM Script Windows pour lancer le frontend
setlocal

cd /d "%~dp0frontend"
echo Demarrage du frontend React sur http://localhost:3000...
call npm run dev

pause
