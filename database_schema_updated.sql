-- DROPUX Multi-Tenant Database Schema (Updated)
-- ================================================
-- Cada usuario registra SU PROPIA app de MercadoLibre

-- 1. USERS TABLE (Cuentas DROPUX)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    plan VARCHAR(50) DEFAULT 'basic', -- basic, pro, enterprise
    role VARCHAR(50) DEFAULT 'owner', -- owner, admin, operator
    active BOOLEAN DEFAULT true,
    trial_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ML_STORES TABLE (Tiendas ML conectadas por usuario)
CREATE TABLE ml_stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Información de la tienda
    store_name VARCHAR(255), -- Nombre personalizado en DROPUX
    site_id VARCHAR(10), -- MCO, MLC, MLA, MLM, MPE, etc.
    
    -- Credenciales de la app ML (creada por el usuario)
    app_number VARCHAR(255), -- Número de app en ML
    app_id VARCHAR(255) UNIQUE NOT NULL, -- Client ID de ML
    app_secret TEXT NOT NULL, -- Client Secret (encrypted)
    redirect_uri TEXT NOT NULL, -- La URI que DROPUX genera
    
    -- OAuth tokens (después de conectar)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    
    -- Info de ML (obtenida después de conectar)
    ml_user_id BIGINT,
    ml_nickname VARCHAR(255),
    ml_email VARCHAR(255),
    ml_country VARCHAR(50),
    
    -- Estado
    is_connected BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ORDERS TABLE
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ml_store_id UUID REFERENCES ml_stores(id) ON DELETE CASCADE,
    
    -- MercadoLibre order info
    ml_order_id VARCHAR(50) UNIQUE,
    ml_status VARCHAR(50),
    ml_date_created TIMESTAMP,
    ml_date_closed TIMESTAMP,
    
    -- Customer info
    buyer_id VARCHAR(50),
    buyer_nickname VARCHAR(255),
    buyer_email VARCHAR(255),
    buyer_phone VARCHAR(50),
    
    -- Order details
    total_amount DECIMAL(12,2),
    product_cost DECIMAL(12,2),
    shipping_cost DECIMAL(12,2),
    currency_id VARCHAR(10),
    
    -- Shipping info
    shipping_id VARCHAR(50),
    tracking_number VARCHAR(255),
    carrier VARCHAR(100),
    shipping_status VARCHAR(50),
    
    -- DROPUX internal
    profit_margin DECIMAL(12,2),
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PRODUCTS TABLE
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ml_store_id UUID REFERENCES ml_stores(id) ON DELETE CASCADE,
    
    -- ML Product info
    ml_item_id VARCHAR(50) UNIQUE,
    title VARCHAR(500),
    price DECIMAL(12,2),
    category_id VARCHAR(50),
    listing_type VARCHAR(50),
    
    -- Stock
    available_quantity INTEGER,
    sold_quantity INTEGER,
    
    -- Status
    status VARCHAR(50), -- active, paused, closed
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. USER_ACTIVITY_LOG
CREATE TABLE user_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(255), -- login, connect_store, sync_orders, etc.
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_ml_stores_user_id ON ml_stores(user_id);
CREATE INDEX idx_orders_ml_store_id ON orders(ml_store_id);
CREATE INDEX idx_orders_ml_order_id ON orders(ml_order_id);
CREATE INDEX idx_products_ml_store_id ON products(ml_store_id);

-- Row Level Security (RLS)
ALTER TABLE ml_stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Policies: Users only see their own data
CREATE POLICY "Users can manage own stores" ON ml_stores
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can view own orders" ON orders
    FOR ALL USING (
        ml_store_id IN (
            SELECT id FROM ml_stores WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view own products" ON products
    FOR ALL USING (
        ml_store_id IN (
            SELECT id FROM ml_stores WHERE user_id = auth.uid()
        )
    );