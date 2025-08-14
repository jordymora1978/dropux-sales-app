from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample data
users_db = [
    {"id": 1, "email": "admin@sales.com", "password": "admin123", "nombre": "Administrador", "activo": True},
    {"id": 2, "email": "vendedor@sales.com", "password": "venta123", "nombre": "Vendedor", "activo": True}
]

sales_db = [
    {"id": 1, "cliente_id": 1, "producto": "Laptop", "cantidad": 1, "precio": 1500.00, "descuento": 0.0, "total": 1500.00, "fecha": "2024-08-11T10:00:00", "estado": "completada"},
    {"id": 2, "cliente_id": 2, "producto": "Mouse", "cantidad": 2, "precio": 25.00, "descuento": 5.0, "total": 45.00, "fecha": "2024-08-11T11:00:00", "estado": "pendiente"}
]

@app.route('/')
def read_root():
    return jsonify({
        "message": "Sales Backend API v1.0 (Flask)",
        "status": "funcionando",
        "docs": "/docs"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "server": "flask"})

@app.route('/token', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Find user
    user = next((u for u in users_db if u["email"] == username and u["password"] == password), None)
    
    if not user or not user["activo"]:
        return jsonify({"error": "Credenciales incorrectas"}), 401
    
    return jsonify({"access_token": f"flask_token_{user['id']}", "token_type": "bearer"})

@app.route('/ventas')
def get_ventas():
    return jsonify(sales_db)

@app.route('/ventas', methods=['POST'])
def create_venta():
    data = request.get_json()
    
    # Calculate total
    subtotal = data['cantidad'] * data['precio']
    total = subtotal - data.get('descuento', 0)
    
    new_sale = {
        "id": len(sales_db) + 1,
        "cliente_id": data['cliente_id'],
        "producto": data['producto'],
        "cantidad": data['cantidad'],
        "precio": data['precio'],
        "descuento": data.get('descuento', 0),
        "total": total,
        "fecha": "2024-08-11T12:00:00",
        "estado": "pendiente"
    }
    
    sales_db.append(new_sale)
    return jsonify(new_sale)

@app.route('/ventas/<int:venta_id>')
def get_venta(venta_id):
    venta = next((v for v in sales_db if v["id"] == venta_id), None)
    if not venta:
        return jsonify({"error": "Venta no encontrada"}), 404
    return jsonify(venta)

@app.route('/dashboard/stats')
def get_dashboard_stats():
    total_ventas = sum(v["total"] for v in sales_db)
    cantidad_ventas = len(sales_db)
    
    return jsonify({
        "ventas_mes": total_ventas,
        "cantidad_ventas": cantidad_ventas,
        "clientes_nuevos": 2,
        "meta_mes": 75
    })

@app.route('/clientes')
def get_clientes():
    return jsonify([
        {"id": 1, "nombre": "María García", "email": "maria@email.com", "telefono": "+57 300 123 4567"},
        {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com", "telefono": "+57 301 234 5678"}
    ])

if __name__ == '__main__':
    print("="*50)
    print("FLASK SALES BACKEND API")
    print("="*50)
    print("Running on: http://127.0.0.1:5000")
    print("Health check: http://127.0.0.1:5000/health")
    print("Sales data: http://127.0.0.1:5000/ventas")
    print("="*50)
    
    app.run(host='127.0.0.1', port=5000, debug=True)