# DROPUX
**Modern Dropshipping Platform - Amazon to MercadoLibre**

## Overview
DROPUX is the complete modernization of a 7-year proven dropshipping operation (formerly DRAPIFY). Built with Python/FastAPI to handle high-volume cross-border sales from Amazon to MercadoLibre across Latin America.

## Business Scale
- **7 years** of proven dropshipping experience
- **20-100 daily orders** (seasonal variation)
- **4 countries**: Colombia, Chile, Peru + Cross Border Trade
- **Multi-account** MercadoLibre management

## Why DRAPIFY 2.0?

### Problems with legacy system:
- Slow performance & high costs ($900/month)
- No Python ecosystem control
- Cannot implement AI features
- Developer dependency for new features

### DROPUX Solutions:
- Modern Python/FastAPI architecture
- AI-powered customer service
- **<$50/month** operational costs
- Full control & rapid feature development
- Platform-ready for third-party dropshippers

## Target Users
- **Master Admin**: Full platform control
- **Admins**: User management & privileges
- **Operators**: Daily order management
- **Third-party Dropshippers**: Limited platform access

## Core Features
- Automated order processing (ML → Anicam → Customer)
- AI customer service with OpenAI
- Real-time tracking across logistics providers
- Multi-country, multi-currency support
- Scalable for platform business model

## Architecture Note
DROPUX uses a microservices architecture:
- **Sales-App**: Order management & operations (this repo)
- **Products-App**: 3M+ products catalog (separate repo/deployment)

---

## 🌐 Production API - FULLY OPERATIONAL

**DROPUX está completamente funcional en producción! 🎉**

### 🔗 URLs Principales
- **Frontend App**: https://sales.dropux.co
- **Backend API**: https://api.dropux.co  
- **Health Check**: https://api.dropux.co/health
- **API Documentation**: https://api.dropux.co/docs
- **Interactive API**: https://api.dropux.co/redoc

### 🔐 Authentication Endpoints
- **Login**: `POST /auth/login`
- **Verify Token**: `GET /auth/me`

### 🏪 MercadoLibre Multi-Tenant
- **Setup Store**: `POST /api/ml/stores/setup`
- **List Stores**: `GET /api/ml/stores`
- **OAuth Callback**: `GET /api/ml/callback`

### 📊 Current Status
- ✅ **3 Users**: admin@dropux.co, operador@dropux.co, viewer@dropux.co
- ✅ **1 ML Store**: Todoencargo (Chile)
- ✅ **JWT Auth**: Fully implemented
- ✅ **Database**: Supabase PostgreSQL
- ✅ **Multi-tenant**: Each user manages own ML stores

## 📋 Development & Documentation

### Local Development
```bash
# Backend
cd C:\Users\jordy\proyectos\sales-system
python main.py
# Available at: http://localhost:8000

# Frontend
cd C:\Users\jordy\proyectos\sales-system\frontend
npm start
# Available at: http://localhost:3000
```

### Documentation
- [📋 Complete Architecture](ARQUITECTURA_SALES_APP.md)
- [🚀 Deployment Guide](QUICK_START_GUIDE.md)

## 🚀 Deployment Status - PRODUCTION READY ✅

### **FASE 1 & 2 - INFRAESTRUCTURA Y FRONTEND (100% COMPLETADA)**
- ✅ **Frontend App**: Live on Vercel at https://sales.dropux.co
- ✅ **Backend API**: Live on Railway at https://api.dropux.co (puerto 8080)
- ✅ **Domain Management**: Subdominios profesionales configurados
- ✅ **Database**: Supabase PostgreSQL conectada y operativa
- ✅ **Authentication**: JWT Bearer token system funcionando end-to-end
- ✅ **Multi-tenant**: ML stores por usuario implementado
- ✅ **GitHub Integration**: Auto-deploy en Railway y Vercel
- ✅ **Environment Variables**: Producción configurada correctamente
- ✅ **CORS Professional**: Configuración específica de dominios
- ✅ **SSL Certificates**: Válidos y operativos
- ✅ **Healthcheck Monitoring**: Configurado y funcional

### **FASE 3 - INTEGRACIÓN MERCADOLIBRE (95% COMPLETADA)** 🎉
- ✅ **OAuth MercadoLibre Profesional**: Sistema completo multi-tenant
- ✅ **Conexión Exitosa**: Primera tienda ML conectada (Todoencargo-co Colombia)
- ✅ **Callback Endpoint**: HTML profesional con auto-redirect y comunicación popup
- ✅ **Exchange Tokens**: Code por access_token funcionando
- ✅ **Refresh Tokens**: Sistema automático implementado
- ✅ **Encrypt Secrets**: App secrets encriptados con Fernet
- ✅ **Multi-país**: Colombia, Chile, Perú configurados
- ✅ **Delete Stores**: Botón eliminar tiendas implementado
- ✅ **UX Profesional**: Popup único controlado, sin ventanas múltiples
- ✅ **JWT Persistencia**: Token persiste al refrescar con expiración a las 23:59

### **DATOS OPERATIVOS ACTUALES - 15 AGOSTO 2025**
- 👥 **3 usuarios activos** con roles diferenciados
- 🏪 **1 tienda ML conectada** (Todoencargo-co - Colombia con App ID: 6996757760934434)
- 📊 **Sistema completamente funcional y profesional**
- ⚡ **Performance óptimo**: <200ms response time
- 🔐 **Seguridad**: JWT con expiración diaria, secrets encriptados, CSRF protection
- 🎨 **UX Mejorado**: Control total de popups, feedback visual claro

## 🎯 PRÓXIMAS TAREAS - FASE FINAL

### **🔄 Prioridad Inmediata**
1. **Completar Integración ML**
   - ⏳ Wrapper para llamadas ML API con tokens de usuario
   - ⏳ Obtener órdenes reales de ML
   - ⏳ Prevenir cuentas duplicadas en dashboard

2. **Sistema de Órdenes Real**
   - ❌ Endpoints CRUD para órdenes
   - ❌ Sincronización con ML API en tiempo real
   - ❌ Reemplazar mockdata con datos reales de producción

### **⏳ Funcionalidades Avanzadas**
- Sistema de Webhooks ML
- Integración Logística (Anicam/Chilexpress)
- Customer Service AI (OpenAI)
- WhatsApp Integration (ChatWook)# Railway Force Deploy Fri, Aug 15, 2025  1:17:27 PM
