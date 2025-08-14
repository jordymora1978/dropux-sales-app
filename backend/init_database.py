"""
Script para inicializar las tablas en Supabase
Ejecutar una sola vez para crear la estructura de la base de datos
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos y configuración
from models.database import engine, Base
from models.tables import (
    User, Company, MLAccount, MLOrder, 
    Shipment, LogisticsProvider, Cliente, Venta
)

def create_all_tables():
    """Crear todas las tablas en Supabase"""
    print("Iniciando creacion de tablas en Supabase...")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("OK - Tablas creadas exitosamente:")
        print("  - users")
        print("  - companies") 
        print("  - ml_accounts")
        print("  - ml_orders")
        print("  - shipments")
        print("  - logistics_providers")
        print("  - clientes")
        print("  - ventas")
        
    except Exception as e:
        print(f"ERROR al crear tablas: {e}")
        sys.exit(1)

def verify_connection():
    """Verificar conexión a la base de datos"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"OK - Conectado a PostgreSQL")
            print(f"Version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"ERROR de conexion: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("INICIALIZACION DE BASE DE DATOS - DRAPIFY 2.0")
    print("=" * 50)
    
    # Verificar conexión
    if verify_connection():
        # Crear tablas
        create_all_tables()
        print("\nBase de datos lista para usar!")
    else:
        print("\nNo se pudo conectar a Supabase")
        print("Verifica tu DATABASE_URL en el archivo .env")