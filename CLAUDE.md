# 🎯 INSTRUCCIONES CLAUDE CODE - PROYECTO DROPUX

## 📋 ESTÁNDARES DE CÓDIGO OBLIGATORIOS

### 🐍 **PYTHON 3.12 TYPE HINTING**
- **OBLIGATORIO**: Usar syntax nativa Python 3.12
- **Union types**: `str | int` en lugar de `Union[str, int]`
- **Generics**: `list[str]` en lugar de `List[str]`
- **Type statements**: `type UserID = int` para aliases
- **Todas las funciones** deben tener tipos de retorno
- **Todos los parámetros** deben estar tipados

### ⚡ **FASTAPI PATTERNS**
```python
# ✅ TEMPLATE OBLIGATORIO para endpoints
@app.post("/api/endpoint")
def endpoint_name(
    request: RequestModel,
    current_user: AuthenticatedUser = Depends(verify_token)
) -> ResponseModel:
    """
    Descripción del endpoint.
    
    Args:
        request: Datos de entrada
        current_user: Usuario autenticado
        
    Returns:
        Respuesta del endpoint
        
    Raises:
        HTTPException: 401/403/500 según error
    """
```

### 🔐 **SEGURIDAD**
- **JWT tokens**: Verificar en todos los endpoints protegidos
- **Validación**: Usar Pydantic para validar datos de entrada
- **Sanitización**: Limpiar inputs antes de usar en base de datos
- **Errores**: NO exponer información sensible en mensajes

### 📊 **BASE DE DATOS**
- **Tipos explícitos**: `type StoreRecord = dict[str, str | int | None]`
- **Error handling**: Manejar excepciones de Supabase
- **Validación**: Verificar que los datos existen antes de usar

### 🧪 **TESTING**
- **Funciones de test** con tipos de retorno `-> None`
- **Mock data** tipado correctamente
- **Assertions** específicas y claras

## 🚨 **REGLAS DE CALIDAD**

### ❌ **PROHIBIDO**
- `from typing import List, Dict, Tuple, Union, Optional`
- Funciones sin tipo de retorno
- Variables sin tipo en operaciones complejas
- Hardcoded secrets o passwords
- Commits sin verificar lint/typecheck

### ✅ **OBLIGATORIO**
- Aplicar **TODOS** los patrones del archivo `PYTHON_CODING_STANDARDS.md`
- Verificar que el código pasa `mypy` (si está configurado)
- Docstrings con Args, Returns, Raises
- Exception handling tipado
- Pydantic models para requests/responses

## 🎯 **PROYECTO ESPECÍFICO**

### **Backend (FastAPI + Supabase)**
- Base URL: `https://sales.dropux.co`
- Database: Supabase PostgreSQL
- Auth: JWT con roles (master_admin, operator, viewer)
- Integración: MercadoLibre API

### **Frontend (React)**
- Deploy: Vercel
- Auth: JWT tokens en localStorage
- API calls: Axios/fetch a backend

### **Usuarios de prueba**
- `admin@dropux.co` / `admin123` (master_admin)
- `operador@dropux.co` / `admin123` (operator)  
- `viewer@dropux.co` / `admin123` (viewer)

## 📋 **CHECKLIST PRE-COMMIT**

Antes de cada commit verificar:
- [ ] Tipos Python 3.12 aplicados correctamente
- [ ] Funciones con docstrings completas
- [ ] Error handling implementado
- [ ] Tests pasando (si existen)
- [ ] Lint/typecheck sin errores
- [ ] Variables de entorno no hardcodeadas
- [ ] Logs no exponen información sensible

## 🔄 **COMANDOS ÚTILES**

```bash
# Backend
cd C:\Users\jordy\proyectos\sales-system
python -m uvicorn main:app --reload

# Frontend  
cd C:\Users\jordy\proyectos\sales-system\frontend
npm start

# Deploy Frontend
npx vercel --prod
```

---

**🎯 CLAUDE**: Siempre aplica estos estándares. Si no cumples alguna regla, el usuario debe recordártelo y tú debes corregir inmediatamente.

**📅 Creado**: 15 de Agosto, 2025  
**🔄 Versión**: 1.0  
**📊 Proyecto**: DROPUX Sales System