@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo Python no fue encontrado.
  echo Instala Python 3.11 o 3.12 y vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno privado de AuraAgenda...
  python -m venv .venv
  if errorlevel 1 (
    echo No se pudo crear el entorno virtual.
    pause
    exit /b 1
  )
)

".venv\Scripts\python.exe" -c "import PySide6, cryptography" >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias de AuraAgenda dentro de .venv...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo No se pudieron instalar las dependencias.
    pause
    exit /b 1
  )
)

".venv\Scripts\python.exe" launcher.py
if errorlevel 1 pause
endlocal
