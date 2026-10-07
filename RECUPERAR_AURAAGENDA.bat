@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecuta INICIAR_AURAAGENDA.bat para preparar el entorno.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" recovery_launcher.py
if errorlevel 1 pause
endlocal
