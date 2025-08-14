@echo off
echo ================================================
echo EJECUTAR COMO ADMINISTRADOR
echo ================================================
echo Iniciando servidor con permisos elevados...
cd /d "%~dp0"
call venv\Scripts\activate
python flask_server.py
pause