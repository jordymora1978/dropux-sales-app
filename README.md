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
- **API Base**: https://sales.dropux.co
- **Health Check**: https://sales.dropux.co/health
- **API Documentation**: https://sales.dropux.co/docs
- **Interactive API**: https://sales.dropux.co/redoc

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

## 🚀 Deployment Status - COMPLETED ✅

- ✅ **Backend API**: Live on Railway with auto-deploy
- ✅ **Domain**: sales.dropux.co with SSL certificate
- ✅ **Database**: Supabase PostgreSQL connected
- ✅ **Authentication**: JWT Bearer token system
- ✅ **Multi-tenant**: ML stores per user
- ✅ **GitHub Integration**: Auto-deploy on push
- ✅ **Environment Variables**: Production configured

## 🎯 Next Phase
- Frontend deployment (React → Vercel/Netlify)
- Complete ML OAuth flow
- Order management dashboard
- Customer service AI integration