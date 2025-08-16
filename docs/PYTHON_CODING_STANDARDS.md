# 📋 PYTHON 3.12 CODING STANDARDS - DROPUX

## 🎯 **Objetivo**
Estas instrucciones garantizan código Python 3.12 profesional con type hinting moderno para el proyecto DROPUX, optimizado para FastAPI y Pydantic.

## 📌 **REGLAS OBLIGATORIAS**

### 1. **Type Statements (Python 3.12)**
```python
# ✅ CORRECTO - Usa 'type' para aliases complejos
type UserID = int
type StoreData = dict[str, str | int | None]
type APIResponse[T] = dict[str, T | str]
type DatabaseRow = dict[str, Any]

# ❌ INCORRECTO - No uses typing.TypeAlias
from typing import TypeAlias
UserID: TypeAlias = int  # Obsoleto en 3.12
```

### 2. **Genéricos Modernos**
```python
# ✅ CORRECTO - Sintaxis nativa 3.12
def get_stores() -> list[Store]:
def process_data(data: dict[str, Any]) -> tuple[bool, str]:
def cache_results() -> set[int]:

# ❌ INCORRECTO - typing module obsoleto
from typing import List, Dict, Tuple, Set
def get_stores() -> List[Store]:
def process_data(data: Dict[str, Any]) -> Tuple[bool, str]:
```

### 3. **Union Types con |**
```python
# ✅ CORRECTO - Operator | 
def authenticate(token: str) -> User | None:
def get_store_id() -> int | str:
def process_response() -> dict[str, Any] | HTTPException:

# ❌ INCORRECTO - typing.Union
from typing import Union, Optional
def authenticate(token: str) -> Optional[User]:
def get_store_id() -> Union[int, str]:
```

## 🚀 **FASTAPI PATTERNS**

### 1. **Endpoint Functions**
```python
# ✅ TEMPLATE OBLIGATORIO para endpoints
@app.post("/api/ml/stores/setup")
def setup_ml_store(
    request: MLStoreSetup,
    current_user: AuthenticatedUser = Depends(verify_token)
) -> MLStoreResponse:
    """
    Create new MercadoLibre store for authenticated user.
    
    Args:
        request: Store configuration data
        current_user: JWT verified user data
        
    Returns:
        Store creation response with OAuth URL
        
    Raises:
        HTTPException: 403 if user lacks permissions
        HTTPException: 500 if database error
    """
    store_data: StoreCreationData = {
        "user_id": current_user.id,
        "company_id": current_user.company_id,
        "site_id": request.site_id,
        "nickname": request.store_name,
    }
    
    response: SupabaseResponse[StoreRecord] = supabase.table('ml_accounts').insert(store_data).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Store creation failed")
    
    return MLStoreResponse.from_store_record(response.data[0])
```

### 2. **Pydantic Models**
```python
# ✅ CORRECTO - Models con type hints completos
class MLStoreSetup(BaseModel):
    site_id: str  # MLC, MLA, MCO, etc.
    app_id: str
    app_secret: str
    store_name: str = ""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

class MLStoreResponse(BaseModel):
    store_id: int
    auth_url: str
    redirect_uri: str
    message: str
    
    @classmethod
    def from_store_record(cls, record: StoreRecord) -> "MLStoreResponse":
        return cls(
            store_id=record["id"],
            auth_url=f"https://auth.mercadolibre.com/{record['site_id'].lower()}/authorization",
            redirect_uri="https://sales.dropux.co/api/ml/callback",
            message=f"Store '{record['nickname']}' created successfully"
        )
```

### 3. **Database Operations**
```python
# ✅ TEMPLATE para operaciones Supabase
type SupabaseResponse[T] = Any  # Hasta que tengamos typing oficial
type StoreRecord = dict[str, str | int | None]
type UserRecord = dict[str, str | int | bool]

async def get_user_stores(user_id: int) -> list[StoreRecord]:
    """Get all ML stores for a specific user."""
    response: SupabaseResponse[list[StoreRecord]] = (
        supabase
        .table('ml_accounts')
        .select("*")
        .eq('user_id', user_id)
        .execute()
    )
    
    return response.data or []

def create_store_record(data: StoreCreationData) -> StoreRecord | None:
    """Create new store record in database."""
    response: SupabaseResponse[list[StoreRecord]] = (
        supabase
        .table('ml_accounts')
        .insert(data)
        .execute()
    )
    
    return response.data[0] if response.data else None
```

## 🔐 **AUTHENTICATION PATTERNS**

### 1. **JWT Functions**
```python
type JWTPayload = dict[str, str | int]
type TokenData = dict[str, Any]

def create_jwt_token(user_data: UserRecord) -> str:
    """Create JWT token for authenticated user."""
    payload: JWTPayload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "company_id": user_data["company_id"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Verify JWT token and return user data."""
    try:
        payload: TokenData = jwt.decode(
            credentials.credentials, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2. **User Models**
```python
class AuthenticatedUser(BaseModel):
    id: int
    email: str
    role: str
    company_id: int
    
    @property
    def is_admin(self) -> bool:
        return self.role == "master_admin"
    
    @property
    def can_manage_stores(self) -> bool:
        return self.role in ["master_admin", "operator"]

class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
    expires_in: int = 86400  # 24 hours
```

## 📊 **ERROR HANDLING**

### 1. **Exception Classes**
```python
class DropuxError(Exception):
    """Base exception for DROPUX application."""
    
    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DatabaseError(DropuxError):
    """Database operation failed."""
    pass

class AuthenticationError(DropuxError):
    """Authentication or authorization failed."""
    pass

class MLIntegrationError(DropuxError):
    """MercadoLibre API integration error."""
    
    def __init__(self, message: str, ml_error_code: str | None = None) -> None:
        super().__init__(message, f"ML_{ml_error_code}")
        self.ml_error_code = ml_error_code
```

### 2. **Error Responses**
```python
def handle_database_error(error: Exception) -> HTTPException:
    """Convert database errors to HTTP responses."""
    error_message: str = str(error)
    
    if "duplicate key" in error_message.lower():
        return HTTPException(
            status_code=409,
            detail="Resource already exists"
        )
    
    return HTTPException(
        status_code=500,
        detail="Database operation failed"
    )
```

## 🧪 **TESTING PATTERNS**

```python
# ✅ Test functions con tipos
def test_create_ml_store() -> None:
    """Test ML store creation endpoint."""
    request_data: dict[str, str] = {
        "site_id": "MLC",
        "app_id": "test_app",
        "app_secret": "test_secret",
        "store_name": "Test Store"
    }
    
    mock_user: AuthenticatedUser = AuthenticatedUser(
        id=1,
        email="test@dropux.co",
        role="master_admin",
        company_id=1
    )
    
    response: MLStoreResponse = setup_ml_store(
        MLStoreSetup(**request_data),
        mock_user
    )
    
    assert response.store_id > 0
    assert "Test Store" in response.message
```

## 📋 **TYPE DEFINITIONS**

```python
# ✅ Definiciones centralizadas
type UserID = int
type CompanyID = int
type StoreID = int
type SiteID = str  # MLC, MLA, MCO, etc.

type StoreCreationData = dict[str, str | int]
type StoreRecord = dict[str, str | int | None | bool]
type UserRecord = dict[str, str | int | bool]
type APIErrorResponse = dict[str, str]

type DatabaseResponse[T] = dict[str, T | list[T] | None]
type SupabaseResponse[T] = Any  # Temporal hasta typing oficial

# Enums para valores fijos
from enum import Enum

class MLSite(str, Enum):
    ARGENTINA = "MLA"
    BRAZIL = "MLB"
    CHILE = "MLC"
    COLOMBIA = "MCO"
    MEXICO = "MLM"
    PERU = "MPE"

class UserRole(str, Enum):
    MASTER_ADMIN = "master_admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
```

## ⚡ **PERFORMANCE PATTERNS**

```python
# ✅ Async operations con tipos
async def bulk_update_stores(
    store_updates: list[dict[str, Any]]
) -> list[StoreRecord]:
    """Update multiple stores concurrently."""
    
    async def update_single_store(update_data: dict[str, Any]) -> StoreRecord | None:
        # Implementación async
        pass
    
    tasks: list[Coroutine[Any, Any, StoreRecord | None]] = [
        update_single_store(update) 
        for update in store_updates
    ]
    
    results: list[StoreRecord | None] = await asyncio.gather(*tasks)
    
    return [result for result in results if result is not None]
```

## ✅ **CHECKLIST DE CALIDAD**

Antes de commitear código, verificar:

- [ ] Todas las funciones tienen tipos de retorno
- [ ] Parámetros de función tipados completamente
- [ ] Variables complejas tienen type hints
- [ ] Usar `|` en lugar de `Union`
- [ ] Usar `list[T]` en lugar de `List[T]`
- [ ] Type statements para aliases complejos
- [ ] Docstrings con Args, Returns, Raises
- [ ] Exception handling tipado
- [ ] Pydantic models validados
- [ ] FastAPI endpoints documentados

---

**🎯 Estas instrucciones garantizan código Python 3.12 profesional, mantenible y robusto para DROPUX en producción.**

**📅 Creado:** 15 de Agosto, 2025  
**📊 Proyecto:** DROPUX Sales System  
**🔄 Versión:** 1.0