@echo off
setlocal EnableExtensions
chcp 65001 >nul

echo ==============================================
echo AuraAgenda V2.0.3 - Aplicar parche CI / Ruff
echo ==============================================
echo.
echo Pega la ruta COMPLETA de la carpeta raiz de AuraAgenda.
echo Ejemplo: C:\Users\TuUsuario\Documents\auraagenda
echo.
set /p "TARGET=Ruta: "
set "TARGET=%TARGET:\"=%"

if not exist "%TARGET%\app\main_window.py" (
    echo.
    echo ERROR: No parece ser la carpeta raiz de AuraAgenda.
    echo Debe contener app\main_window.py, README.md y tests\.
    pause
    exit /b 1
)

if not exist "%~dp0PATCH_FILES\app\main_window.py" (
    echo.
    echo ERROR: No se encontro PATCH_FILES junto a este archivo.
    pause
    exit /b 1
)

echo.
echo Copiando archivos corregidos...
xcopy "%~dp0PATCH_FILES\*" "%TARGET%\" /E /I /Y >nul
if errorlevel 1 (
    echo ERROR: No se pudo copiar el parche.
    pause
    exit /b 1
)

echo.
echo Parche copiado correctamente.
echo.
pushd "%TARGET%"
python -m compileall -q .
if errorlevel 1 (
    echo ADVERTENCIA: compileall encontro un error. No hagas push todavia.
) else (
    echo compileall: OK
)

echo.
git status --short
popd

echo.
echo Siguiente paso recomendado desde CMD en AuraAgenda:
echo   git add .
echo   git commit -m "Fix Ruff CI errors in AuraAgenda v2.0.3"
echo   git push
echo.
pause
endlocal
