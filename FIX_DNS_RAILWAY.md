# 🔧 SOLUCIÓN PROBLEMA DNS - API.DROPUX.CO

## 🚨 **PROBLEMA IDENTIFICADO**
El dominio `api.dropux.co` está apuntando al proyecto incorrecto en Railway.

### **Estado Actual:**
- ❌ `api.dropux.co` → `qgdzdx2w.up.railway.app` (Error 405)
- ✅ `web-production-ae7da.up.railway.app` → Backend funcional

## ✅ **SOLUCIÓN PERMANENTE - ACTUALIZAR DNS EN CLOUDFLARE**

### **Paso 1: Acceder a Cloudflare**
1. Ir a [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Seleccionar el dominio `dropux.co`
3. Ir a la sección **DNS**

### **Paso 2: Actualizar registro CNAME**
Buscar el registro `api` y actualizarlo:

```
Tipo: CNAME
Nombre: api
Contenido: web-production-ae7da.up.railway.app
Proxy: ✅ (Activado - nube naranja)
TTL: Auto
```

### **Paso 3: Verificar en Railway**
1. Ir a tu proyecto en [Railway Dashboard](https://railway.app)
2. En Settings → Domains
3. Verificar que `api.dropux.co` esté configurado
4. Si no está, agregar custom domain: `api.dropux.co`

## 🔄 **SOLUCIÓN TEMPORAL (YA APLICADA)**

Mientras se propagan los cambios DNS, el frontend está configurado para usar directamente:
```
REACT_APP_API_URL=https://web-production-ae7da.up.railway.app
```

## 📋 **VERIFICACIÓN POST-CAMBIO**

Una vez actualizado el DNS, verificar con estos comandos:

```bash
# Verificar DNS propagado
nslookup api.dropux.co

# Test del API
curl https://api.dropux.co/health

# Debería responder:
# {"status":"healthy","service":"DROPUX API",...}
```

## 🔄 **CUANDO EL DNS ESTÉ CORREGIDO**

Actualizar los archivos `.env` del frontend:

### **frontend/.env**
```env
REACT_APP_API_URL=https://api.dropux.co
REACT_APP_ENV=production
```

### **frontend/.env.production**
```env
REACT_APP_API_URL=https://api.dropux.co
REACT_APP_ENV=production
```

## 🚀 **DEPLOYMENT DESPUÉS DEL FIX**

```bash
# Frontend (Vercel)
cd frontend
npm run build
npx vercel --prod

# El backend no necesita cambios
```

## 📝 **NOTAS IMPORTANTES**

1. **Propagación DNS**: Los cambios pueden tardar 1-48 horas en propagarse
2. **Cache**: Limpiar cache del navegador después del cambio
3. **CORS**: El backend ya está configurado para aceptar ambos dominios

---

**Fecha**: 15 de Agosto, 2025
**Status**: Solución temporal aplicada, pendiente actualización DNS