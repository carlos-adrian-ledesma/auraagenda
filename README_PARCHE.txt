AURAAGENDA V2.0.3 — PARCHE CI / RUFF
=====================================

Objetivo
--------
Corregir los 37 hallazgos que hicieron fallar el job "Ruff safety lint" de
GitHub Actions en el commit inicial de AuraAgenda v2.0.3.

Hallazgos corregidos
--------------------
- 5 x F601: claves duplicadas en app/i18n/translations.py
- 1 x F841: variable local "close" asignada y no usada
- 31 x F401: imports/re-exports marcados como no usados

Archivos modificados: 11
------------------------
app/i18n/translations.py
app/main_window.py
app/pages/__init__.py
app/pages/calendar.py
app/pages/settings.py
app/pages/statistics.py
app/services/migration.py
app/services/recovery.py
tests/test_backup_hardening.py
tests/test_navigation.py
tests/test_security_recovery.py

FORMA RECOMENDADA: git apply
---------------------------
1. Extrae este ZIP.
2. Copia AuraAgenda_V2.0.3_CI_Ruff_Fix.patch dentro de la carpeta raiz del
   repositorio AuraAgenda (donde estan README.md, app, tests, etc.).
3. Abre CMD en esa carpeta.
4. Ejecuta:

   git apply --check AuraAgenda_V2.0.3_CI_Ruff_Fix.patch

   Si no aparece ningun error, ejecuta:

   git apply AuraAgenda_V2.0.3_CI_Ruff_Fix.patch

5. Verifica:

   git status
   python -m compileall -q .

   Si ya tienes .venv y requirements-dev instalados:

   .venv\Scripts\python.exe -m ruff check app tests --select F,E9
   .venv\Scripts\python.exe -m unittest discover -s tests -v

6. Si todo esta correcto:

   git add .
   git commit -m "Fix Ruff CI errors in AuraAgenda v2.0.3"
   git push

GitHub Actions se ejecutara automaticamente despues del push.

ALTERNATIVA
-----------
La carpeta PATCH_FILES contiene los 11 archivos corregidos, conservando sus
rutas. Puede usarse como respaldo si git apply no se puede ejecutar.

Validacion realizada antes de empaquetar
----------------------------------------
- python -m compileall -q . : PASS
- 14 tests no-Qt seleccionados: PASS
- las 5 claves duplicadas reportadas fueron eliminadas sin cambiar su valor
  efectivo
- los re-exports de app/pages/__init__.py ahora estan declarados en __all__

Nota
----
Este entorno no tiene Ruff instalado y no tiene acceso de red para instalarlo.
Por eso la comprobacion final de Ruff debe realizarla GitHub Actions despues del
push. El parche fue construido directamente contra los 37 diagnosticos exactos
reportados por el workflow actual.
