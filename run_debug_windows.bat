@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta .venv. Ejecuta INICIAR_AURAAGENDA.bat.
  pause
  exit /b 1
)
set QT_DEBUG_PLUGINS=0
".venv\Scripts\python.exe" launcher.py
pause
endlocal
