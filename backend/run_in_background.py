#!/usr/bin/env python3
"""
Script para ejecutar el servidor en segundo plano
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_background_server():
    """Ejecutar servidor en segundo plano"""
    script_dir = Path(__file__).parent
    flask_script = script_dir / "flask_server.py"
    venv_python = script_dir / "venv" / "Scripts" / "python.exe"
    
    print("="*50)
    print("SERVIDOR EN SEGUNDO PLANO")
    print("="*50)
    print(f"Iniciando servidor Flask...")
    print(f"URL: http://127.0.0.1:5000")
    print(f"PID será mostrado para poder detenerlo después")
    print("="*50)
    
    try:
        # Ejecutar el servidor en segundo plano
        process = subprocess.Popen(
            [str(venv_python), str(flask_script)],
            cwd=str(script_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE,  # Nueva ventana
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Servidor iniciado en segundo plano")
        print(f"✅ Process ID (PID): {process.pid}")
        print(f"✅ URL: http://127.0.0.1:5000")
        print()
        print("Para detener el servidor:")
        print(f"  taskkill /PID {process.pid} /F")
        print()
        print("O usa el Administrador de Tareas")
        
        # Esperar un poco para verificar que inició bien
        time.sleep(3)
        if process.poll() is None:
            print("✅ Servidor corriendo correctamente")
            
            # Crear archivo con el PID para fácil acceso
            with open(script_dir / "server_pid.txt", "w") as f:
                f.write(str(process.pid))
            print(f"✅ PID guardado en: server_pid.txt")
        else:
            print("❌ Error: El servidor se detuvo inmediatamente")
            
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    run_background_server()