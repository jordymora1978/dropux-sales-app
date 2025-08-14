@echo off
title Sales Backend API
echo ================================================
echo SALES BACKEND API - INICIO RAPIDO
echo ================================================
echo IMPORTANTE: Ejecutar como ADMINISTRADOR
echo ================================================

cd /d "%~dp0"
call venv\Scripts\activate

echo.
echo Iniciando servidor en http://127.0.0.1:5000...
echo.
echo Endpoints disponibles:
echo   - http://127.0.0.1:5000 (Principal)
echo   - http://127.0.0.1:5000/health (Estado)
echo   - http://127.0.0.1:5000/ventas (Datos)
echo   - http://127.0.0.1:5000/docs (Documentacion)
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================

python flask_server.py