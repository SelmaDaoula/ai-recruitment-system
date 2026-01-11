@echo off
REM Script Windows pour lancer le backend avec l'encodage UTF-8
setlocal enabledelayedexpansion

REM Définir l'encodage UTF-8 pour Python
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

REM Activer l'environnement virtuel et lancer le backend
cd /d "%~dp0backend"
call ..\venv\Scripts\activate.bat
echo Demarrage du backend FastAPI sur http://localhost:8000...
..\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
