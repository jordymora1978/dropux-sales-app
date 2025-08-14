# 🚀 GUÍA RÁPIDA DE INICIO - DROPUX SALES APP

## 🌐 PRODUCCIÓN (¡YA DISPONIBLE!)
**DROPUX está funcionando en producción:**

- **API Base**: https://sales.dropux.co
- **Health Check**: https://sales.dropux.co/health
- **API Docs**: https://sales.dropux.co/docs
- **ReDoc**: https://sales.dropux.co/redoc

---

## ⚡ DESARROLLO LOCAL (5 minutos)

### 1. Iniciar Backend API
```bash
📂 Navegar a: C:\Users\jordy\proyectos\sales-system\backend\
💻 Ejecutar: python main.py
✅ Resultado: Servidor en http://127.0.0.1:8000
```

### 2. Iniciar Frontend React
```bash
📂 Abrir nueva terminal en: C:\Users\jordy\proyectos\sales-system\frontend\
💻 Ejecutar: npm start
✅ Resultado: App en http://localhost:3000
```

### 3. Verificar Funcionamiento
- ✅ Backend: http://127.0.0.1:8000
- ✅ Frontend: http://localhost:3000
- ✅ API Health: http://127.0.0.1:8000/health
- ✅ API Docs: http://127.0.0.1:8000/docs

## 🔧 ENDPOINTS PRINCIPALES

### Datos de Ventas
```
GET http://127.0.0.1:8000/ventas
POST http://127.0.0.1:8000/ventas
GET http://127.0.0.1:8000/ventas/{id}
```

### MercadoLibre OAuth
```
GET http://127.0.0.1:8000/ml/auth
GET http://127.0.0.1:8000/ml/callback
GET http://127.0.0.1:8000/ml/orders
```

### Dashboard
```
GET http://127.0.0.1:8000/dashboard/stats
GET http://127.0.0.1:8000/clientes
```

## 📋 CONFIGURACIÓN INICIAL

### 1. Variables de Entorno
```bash
# Crear archivo .env en backend/
cp .env.example .env
# Editar con tus credenciales
```

### 2. Base de Datos
```bash
# Las tablas se crean automáticamente al iniciar
# SQLAlchemy + PostgreSQL/Supabase
```

### 3. Dependencias
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 🎯 CREDENCIALES DE PRUEBA
```
Admin: admin@sales.com / admin123
Vendedor: vendedor@sales.com / venta123
```

## ❓ TROUBLESHOOTING

### Puerto ocupado
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Errores de CORS
- Verificar que backend esté corriendo
- Verificar URL en frontend: http://127.0.0.1:8000

### Dependencias faltantes
```bash
pip install -r requirements.txt
npm install
```

## 📞 SOPORTE
- Documentación: Ver ARQUITECTURA_SALES_APP.md
- API Docs: http://127.0.0.1:8000/docs

## 🚀 DEPLOYMENT INFO
- **Platform**: Railway
- **Domain**: sales.dropux.co 
- **SSL**: ✅ Active
- **Status**: ✅ Live in Production
- **GitHub**: https://github.com/jordymora1978/dropux-sales-app

---
**Última actualización:** 14 de Agosto, 2025