-- DROPUX Multi-Tenant Database Schema
-- =====================================

-- 1. USERS TABLE (Master accounts)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- admin, user, operator
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ML_ACCOUNTS TABLE (MercadoLibre connected accounts)
CREATE TABLE ml_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- ML OAuth Credentials (encrypted in production)
    ml_user_id BIGINT UNIQUE,
    nickname VARCHAR(255),
    site_id VARCHAR(10), -- MCO, MLC, MPE, etc.
    
    -- OAuth tokens (encrypted)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    
    -- App credentials (each account has its own)
    client_id VARCHAR(255),
    client_secret TEXT, -- encrypted
    
    -- Account info
    account_name VARCHAR(255), -- Custom name like "Tienda Principal"
    is_active BOOLEAN DEFAULT true,
    is_test_account BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ORDERS TABLE
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ml_account_id UUID REFERENCES ml_accounts(id) ON DELETE CASCADE,
    
    -- MercadoLibre order info
    ml_order_id BIGINT UNIQUE,
    status VARCHAR(50),
    date_created TIMESTAMP,
    date_closed TIMESTAMP,
    
    -- Customer info
    buyer_id BIGINT,
    buyer_nickname VARCHAR(255),
    buyer_email VARCHAR(255),
    
    -- Order details
    total_amount DECIMAL(10,2),
    currency_id VARCHAR(10),
    shipping_cost DECIMAL(10,2),
    
    -- Tracking
    shipping_id BIGINT,
    tracking_number VARCHAR(255),
    carrier VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. APP_CONFIGURATIONS TABLE (Global ML apps registry)
CREATE TABLE app_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    app_name VARCHAR(255) UNIQUE, -- "Todoencargo", "Tienda2", etc.
    client_id VARCHAR(255) UNIQUE,
    client_secret TEXT, -- master encrypted
    redirect_uri TEXT,
    scopes TEXT, -- JSON array of scopes
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. USER_SESSIONS TABLE (for JWT tracking)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES for performance
CREATE INDEX idx_ml_accounts_user_id ON ml_accounts(user_id);
CREATE INDEX idx_orders_ml_account_id ON orders(ml_account_id);
CREATE INDEX idx_orders_ml_order_id ON orders(ml_order_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Row Level Security (RLS) for multi-tenancy
ALTER TABLE ml_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own ML accounts
CREATE POLICY "Users can view own ml_accounts" ON ml_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own ml_accounts" ON ml_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own ml_accounts" ON ml_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can only see orders from their ML accounts
CREATE POLICY "Users can view own orders" ON orders
    FOR SELECT USING (
        ml_account_id IN (
            SELECT id FROM ml_accounts WHERE user_id = auth.uid()
        )
    );