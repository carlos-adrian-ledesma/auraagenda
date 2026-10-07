@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

".venv\Scripts\pyinstaller.exe" --noconfirm --clean --windowed ^
  --name "AuraAgenda" ^
  --icon "assets\AuraAgenda.ico" ^
  --add-data "assets;assets" ^
  --collect-all tzdata ^
  --collect-all cryptography ^
  launcher.py
if errorlevel 1 exit /b 1

echo Ejecutable creado en dist\AuraAgenda.exe
endlocal
