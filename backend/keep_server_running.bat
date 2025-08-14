@echo off
title Sales Backend API - MANTENER ABIERTO
color 0A
echo ================================================
echo SALES BACKEND API SERVER
echo ================================================
echo IMPORTANTE: NO CERRAR ESTA VENTANA
echo El servidor se detendra si cierras esta ventana
echo ================================================

cd /d "%~dp0"
call venv\Scripts\activate

:RESTART
echo.
echo [%TIME%] Iniciando servidor...
echo URL: http://127.0.0.1:5000
echo ================================================
echo Minimiza esta ventana (no la cierres)
echo ================================================

python flask_server.py

echo.
echo [%TIME%] Servidor detenido
echo ================================================
echo Presiona cualquier tecla para REINICIAR el servidor
echo O cierra esta ventana para DETENER completamente
echo ================================================
pause >nul
goto RESTART