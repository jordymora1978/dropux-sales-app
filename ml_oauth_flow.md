# 🔐 MercadoLibre OAuth Flow - Multi-Tenant

## Flujo de Conexión de Cuentas ML

### 1. Usuario hace login en DROPUX
```
POST /api/auth/login
{
    "email": "jordy@dropux.co",
    "password": "******"
}
→ Returns: JWT token
```

### 2. Usuario va a "Conectar Nueva Tienda ML"
```
GET /api/ml/available-apps
→ Returns: Lista de apps ML disponibles para conectar
[
    {
        "id": "uuid",
        "app_name": "Todoencargo",
        "client_id": "6996757760934434"
    }
]
```

### 3. Usuario selecciona app y país
```
POST /api/ml/initiate-oauth
{
    "app_configuration_id": "uuid",
    "site_id": "MCO", // Colombia
    "account_name": "Mi Tienda Principal"
}
→ Returns: OAuth URL personalizada
```

### 4. Redirect a MercadoLibre
```
https://auth.mercadolibre.com.co/authorization?
    response_type=code&
    client_id=6996757760934434&
    redirect_uri=https://sales.dropux.co/api/ml/callback&
    state={encrypted_user_id_and_session}
```

### 5. Callback después de autorización
```
GET /api/ml/callback?code=xxx&state=xxx
→ Decodifica state para identificar usuario
→ Intercambia code por tokens
→ Guarda en ml_accounts tabla:
    - user_id (del state)
    - access_token
    - refresh_token
    - ml_user_id
    - nickname
    - client_id (de app_configuration)
```

### 6. Usuario ve sus tiendas conectadas
```
GET /api/ml/my-accounts
→ Returns: Solo las cuentas ML del usuario autenticado
[
    {
        "id": "uuid",
        "account_name": "Mi Tienda Principal",
        "nickname": "TODOENCARGO",
        "site_id": "MCO",
        "is_active": true
    }
]
```

## 🔑 Puntos Clave:

1. **Variables de entorno**: Solo para TU app Todoencargo
2. **Base de datos**: Guarda credentials de CADA usuario
3. **JWT**: Identifica qué usuario está haciendo requests
4. **RLS (Row Level Security)**: Aísla datos entre usuarios
5. **State parameter**: Crucial para identificar usuario en callback

## Diferencia con Variables de Entorno:

❌ **INCORRECTO**: Variables de entorno para cada cuenta
```env
ML_CLIENT_ID_USER1=xxx
ML_CLIENT_ID_USER2=xxx  
```

✅ **CORRECTO**: Variables solo para app master
```env
# Solo para tu app Todoencargo (master)
ML_MASTER_CLIENT_ID=6996757760934434
ML_MASTER_CLIENT_SECRET=xxx

# Las demás credentials van en DB
```