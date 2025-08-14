# 📋 ARQUITECTURA COMPLETA - SALES APPLICATION

## 🏗️ ARQUITECTURA DE MICROSERVICIOS

### Sistema dividido en 2 aplicaciones independientes:

**1. SALES-APP (Esta documentación)**
- URL: sales.midominio.com
- BD: Supabase Proyecto 1
- Función: Ventas, órdenes, mensajes, tracking
- Datos: Operaciones diarias (calientes)

**2. PRODUCTS-APP (App complementaria - documentación separada)**
- URL: products.midominio.com  
- BD: Supabase Proyecto 2
- Función: Catálogo 3M productos, fichas técnicas, inventario
- Datos: Consultas según demanda (fríos)

### Comunicación entre apps:
```
Sales-App → API REST → Products-App
Ejemplo: Obtener ficha técnica para responder pregunta cliente
```

## 🏗️ ESTRUCTURA GENERAL DEL PROYECTO (SALES-APP)

```
C:\Users\jordy\proyectos\sales-system\
├── backend/                # Backend API (FastAPI/Python)
│   ├── models/            # SQLAlchemy models
│   │   ├── database.py    # Database configuration
│   │   └── tables.py      # Table definitions
│   ├── services/          # Business logic
│   │   ├── mercadolibre.py # ML OAuth integration
│   │   └── logistics.py   # Anicam & Chilexpress APIs
│   ├── main.py            # FastAPI con Supabase
│   ├── flask_server.py    # Servidor Flask alternativo
│   ├── requirements.txt   # Dependencias Python
│   ├── .env.example       # Variables de entorno ejemplo
│   └── auth.py            # Autenticación JWT
│
└── frontend/              # Frontend React
    ├── src/
    │   ├── App.js         # Componente principal
    │   ├── App.css        # Estilos Tailwind
    │   └── index.js       # Punto de entrada
    ├── package.json       # Dependencias React
    ├── public/
    └── node_modules/
```

## 🔧 TECNOLOGÍAS IMPLEMENTADAS

### Backend (Puerto 8000) ✅ FUNCIONANDO
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy
- **Base de datos:** PostgreSQL (Supabase)
- **Autenticación:** JWT tokens
- **CORS:** Habilitado para React
- **Integraciones:**
  - MercadoLibre OAuth
  - Anicam Logistics API
  - Chilexpress API

### Frontend (Puerto 3000) ✅ FUNCIONANDO
- **Framework:** React
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Testing:** Jest + React Testing Library
- **Build:** Create React App

## 🌐 API ENDPOINTS DISPONIBLES

### Autenticación
```http
POST http://127.0.0.1:8000/token
Content-Type: application/json
{
  "username": "admin@sales.com",
  "password": "admin123"
}
```

### Ventas
```http
GET http://127.0.0.1:8000/ventas           # Listar ventas
POST http://127.0.0.1:8000/ventas          # Crear venta
GET http://127.0.0.1:8000/ventas/{id}      # Venta específica
```

### MercadoLibre Integration
```http
GET http://127.0.0.1:8000/ml/auth          # OAuth URL
GET http://127.0.0.1:8000/ml/callback      # OAuth callback
GET http://127.0.0.1:8000/ml/orders        # Get ML orders
```

### Dashboard
```http
GET http://127.0.0.1:8000/dashboard/stats  # Estadísticas
GET http://127.0.0.1:8000/clientes         # Lista clientes
GET http://127.0.0.1:8000/health           # Estado servidor
```

## 📊 MODELOS DE DATOS (SQLAlchemy)

### Usuario
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    role = Column(String(50))
```

### ML Account
```python
class MLAccount(Base):
    __tablename__ = "ml_accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    site_id = Column(String(10))  # MLA, MCO, MLC
    access_token = Column(Text)
    refresh_token = Column(Text)
```

### Shipment
```python
class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("ml_orders.id"))
    provider_id = Column(Integer, ForeignKey("logistics_providers.id"))
    tracking_number = Column(String(255))
    status = Column(String(50))
```

## 🚀 PROCESO DE INICIO

### 1. Backend
```bash
cd C:\Users\jordy\proyectos\sales-system\backend
python main.py
# Servidor disponible en: http://127.0.0.1:8000
```

### 2. Frontend
```bash
cd C:\Users\jordy\proyectos\sales-system\frontend
npm start
# Disponible en: http://localhost:3000
```

## 🔐 CONFIGURACIÓN DE SEGURIDAD

### Variables de Entorno (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
ML_CLIENT_ID=your-ml-client-id
ML_CLIENT_SECRET=your-ml-client-secret
ANICAM_API_KEY=your-anicam-key
CHILEXPRESS_API_KEY=your-chilexpress-key
```

## ⚠️ ESTRATEGIA DE MIGRACIÓN (CONFIDENCIAL)

### Desarrollo en Paralelo - NO TOCAR PRODUCCIÓN
- **Versión actual**: drapify.co en DigitalOcean ($290/mes) - NO TOCAR
- **Versión nueva**: DRAPIFY 2.0 completamente independiente
- **Estrategia**: Desarrollo stealth hasta estar 100% listo

### Configuración Independiente Requerida:
1. **Nueva App MercadoLibre Developers** (no usar la de producción)
   - Nombre diferente (ej: "SalesManager Pro")
   - CLIENT_ID y CLIENT_SECRET propios
   - Las cuentas ML pueden estar en ambas apps simultáneamente
   
2. **Infraestructura Nueva:**
   - Supabase (no DigitalOcean)
   - Railway/Vercel para deployment
   - Dominio temporal hasta migración final

3. **Migración Final (cuando esté listo):**
   - Un día simplemente cambiar DNS
   - Apagar DigitalOcean
   - Ahorro inmediato de $245/mes

## 📊 ESTADO DE IMPLEMENTACIÓN

### ✅ COMPLETADO - DROPUX BÁSICO FUNCIONANDO
- ✅ Backend FastAPI básico con Supabase PostgreSQL
- ✅ Base de datos profesional multi-tenant (8 tablas)
- ✅ Autenticación JWT con roles (master_admin, operator, viewer)
- ✅ Modelos SQLAlchemy conectados y funcionando
- ✅ Frontend React completo y funcional
- ✅ App MercadoLibre "Todoencargo Sales App" creada
- ✅ OAuth MercadoLibre funcionando (CLIENT_ID: 6996757760934434)
- ✅ Endpoints ML: /ml/auth, /ml/callback, /webhooks/ml
- ✅ Configuración para sales.dropux.co
- ✅ CORS configurado correctamente

### 🚀 EN PROCESO - DEPLOY A PRODUCCIÓN
- 🔄 Crear repositorio GitHub
- ⏳ Subir código a GitHub
- ⏳ Deploy a Railway
- ⏳ Configurar dominio sales.dropux.co
- ⏳ Variables de entorno en producción
- ⏳ Probar OAuth en producción

### 📝 PENDIENTE - FUNCIONALIDADES AVANZADAS
- ⏳ Gestión completa de órdenes ML
- ⏳ Sistema de webhooks automáticos
- ⏳ Integración OpenAI para customer service
- ⏳ Conectar con Anicam/Chilexpress APIs
- ⏳ ChatWook para WhatsApp
- ⏳ Dashboard con métricas reales

### 🔧 PENDIENTE

#### 1. Sistema de Webhooks ML
- Recibir órdenes automáticamente cuando alguien compra
- Endpoint `/webhooks/mercadolibre`
- Procesar orden → crear en Anicam

#### 2. Integración OpenAI Completa
- Responder preguntas clientes automáticamente
- Analizar problemas en órdenes
- Generar mensajes personalizados

#### 3. Flujo Completo Sales
- ML Order → Crear en Anicam → Tracking → Mensaje cliente
- Actualmente solo tienes piezas separadas

#### 4. Modelos de Datos Faltantes
- Orders (órdenes ML completas)
- Messages (comunicación con clientes)
- Tracking (seguimiento logístico)

#### 5. MercadoPago API
- Verificar pagos antes de procesar órdenes

#### 6. ChatWook - Integración WhatsApp
- Contactar clientes por fuera de MercadoLibre
- Comunicación directa por WhatsApp (estándar en Latinoamérica)
- Automatización de mensajes de seguimiento

#### 7. Sistema de Páginas del Menú
- **Órdenes** (principal) - Ya implementado con datos mock
- **Dashboard** - Estadísticas y métricas importantes
- **Mensajería** - Comunicación centralizada con clientes
- **Preguntas** - Gestión de Q&A de productos
- **Configuración** - Módulo complejo con:
  - Fórmulas de precios por cuenta ML
  - API keys (OpenAI, ChatWook, etc.)
  - Sistema de privilegios por usuario
  - Features pagadas (WhatsApp, etc.)

#### 8. Sistema de Privilegios y Roles
- **Master Admin** - Control total del sistema
- **Admins** - Gestión de usuarios y privilegios
- **Operadores** - Acceso limitado a operaciones diarias
- **Third-party** - Acceso restringido según suscripción

#### 9. Configuración General
- Configurar credenciales reales
- Pruebas de integración
- Deploy a Railway

## 📈 PRÓXIMOS PASOS

### Fase 1: Configuración
1. Configurar .env con credenciales reales
2. Conectar con base de datos PostgreSQL
3. Probar integraciones ML y logística

### Fase 2: Deploy
1. Push a GitHub
2. Configurar Railway
3. Variables de entorno en producción

## 📝 COMANDOS ÚTILES

### Backend
```bash
# Instalar dependencias
cd backend
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

### Frontend
```bash
# Instalar dependencias
cd frontend
npm install

# Ejecutar desarrollo
npm start

# Build producción
npm run build
```

---

**📅 Última actualización:** 12 de Agosto, 2025
**📊 Estado:** REESTRUCTURADO Y ORGANIZADO ✅
**🎯 Próximo objetivo:** Deploy en Railway con GitHub