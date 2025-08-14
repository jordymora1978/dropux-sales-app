"""
Script para agregar datos de prueba a la base de datos
"""
import sys
from datetime import datetime
from models.database import SessionLocal, engine
from models.tables import Company, User, LogisticsProvider
import hashlib

def hash_password(password: str) -> str:
    """Simple hash para passwords de prueba"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Agregar datos iniciales de prueba"""
    db = SessionLocal()
    
    try:
        print("Agregando datos de prueba...")
        
        # Crear empresa de prueba
        company = Company(
            name="DRAPIFY Demo",
            domain="demo",
            plan="premium",
            active=True
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"  - Empresa creada: {company.name}")
        
        # Crear usuarios de prueba
        users = [
            {
                "email": "admin@drapify.com",
                "password": "admin123",
                "role": "master_admin",
                "company_id": company.id
            },
            {
                "email": "operador@drapify.com", 
                "password": "oper123",
                "role": "operator",
                "company_id": company.id
            },
            {
                "email": "viewer@drapify.com",
                "password": "view123",
                "role": "viewer",
                "company_id": company.id
            }
        ]
        
        for user_data in users:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                company_id=user_data["company_id"],
                active=True
            )
            db.add(user)
            print(f"  - Usuario creado: {user_data['email']} / {user_data['password']}")
        
        # Agregar proveedores logísticos
        providers = [
            {
                "name": "ANICAM",
                "api_endpoint": "https://api.anicam.com/v1",
                "credentials": {"api_key": "test_key_anicam"}
            },
            {
                "name": "CHILEXPRESS",
                "api_endpoint": "https://api.chilexpress.cl/v1",
                "credentials": {"api_key": "test_key_chilexpress"}
            }
        ]
        
        for prov_data in providers:
            provider = LogisticsProvider(**prov_data)
            db.add(provider)
            print(f"  - Proveedor agregado: {prov_data['name']}")
        
        db.commit()
        print("\nDatos de prueba agregados exitosamente!")
        print("\nUsuarios para login:")
        print("  Email: admin@drapify.com / Password: admin123")
        print("  Email: operador@drapify.com / Password: oper123")
        print("  Email: viewer@drapify.com / Password: view123")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("AGREGANDO DATOS DE PRUEBA - DRAPIFY 2.0")
    print("=" * 50)
    seed_database()