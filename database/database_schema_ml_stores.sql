-- MercadoLibre Stores Table for Multi-tenant Architecture
-- Professional implementation with security and performance best practices

CREATE TABLE IF NOT EXISTS public.ml_stores (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- User relationships
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    company_id INTEGER NOT NULL,
    
    -- ML App Configuration (user provided)
    site_id VARCHAR(10) NOT NULL, -- MLC, MCO, MLA, etc.
    app_id VARCHAR(50) NOT NULL, -- ML App ID from developers console
    app_secret_encrypted TEXT NOT NULL, -- Encrypted ML App Secret
    
    -- Store Information
    nickname VARCHAR(255) NOT NULL, -- User-friendly store name
    store_name VARCHAR(255), -- Store display name
    
    -- OAuth Flow Data
    redirect_uri TEXT, -- Generated redirect URI for this store
    state_token TEXT, -- CSRF protection token
    status VARCHAR(50) DEFAULT 'pending_authorization', -- pending_authorization, connected, disconnected, error
    
    -- ML Tokens (sensitive data)
    access_token TEXT, -- ML Access Token (encrypted if needed)
    refresh_token TEXT, -- ML Refresh Token
    token_expires_at TIMESTAMP,
    token_refreshed_at TIMESTAMP,
    
    -- ML User Information
    ml_user_id BIGINT, -- ML User ID (from ML API)
    ml_nickname VARCHAR(255), -- ML Account nickname
    
    -- Connection tracking
    connected_at TIMESTAMP,
    disconnected_at TIMESTAMP,
    last_sync_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_site_app UNIQUE(user_id, site_id, app_id),
    CONSTRAINT valid_site_id CHECK (site_id IN (
        'MLA', 'MLB', 'MCO', 'MCR', 'MEC', 'MLC', 
        'MLM', 'MLU', 'MLV', 'MPA', 'MPE', 'MPT', 'MRD'
    )),
    CONSTRAINT valid_status CHECK (status IN (
        'pending_authorization', 'connected', 'disconnected', 'error', 'expired'
    ))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ml_stores_user_id ON public.ml_stores(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_stores_company_id ON public.ml_stores(company_id);
CREATE INDEX IF NOT EXISTS idx_ml_stores_site_id ON public.ml_stores(site_id);
CREATE INDEX IF NOT EXISTS idx_ml_stores_status ON public.ml_stores(status);
CREATE INDEX IF NOT EXISTS idx_ml_stores_user_site ON public.ml_stores(user_id, site_id);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_ml_stores_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_ml_stores_updated_at ON public.ml_stores;
CREATE TRIGGER trigger_ml_stores_updated_at
    BEFORE UPDATE ON public.ml_stores
    FOR EACH ROW
    EXECUTE FUNCTION update_ml_stores_updated_at();

-- Row Level Security (RLS) for multi-tenant isolation
ALTER TABLE public.ml_stores ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own stores
CREATE POLICY "Users can view own stores" ON public.ml_stores
    FOR SELECT USING (
        user_id = (current_setting('request.jwt.claims', true)::json ->> 'user_id')::int
    );

-- Policy: Users can insert their own stores
CREATE POLICY "Users can insert own stores" ON public.ml_stores
    FOR INSERT WITH CHECK (
        user_id = (current_setting('request.jwt.claims', true)::json ->> 'user_id')::int
    );

-- Policy: Users can update their own stores
CREATE POLICY "Users can update own stores" ON public.ml_stores
    FOR UPDATE USING (
        user_id = (current_setting('request.jwt.claims', true)::json ->> 'user_id')::int
    );

-- Policy: Users can delete their own stores
CREATE POLICY "Users can delete own stores" ON public.ml_stores
    FOR DELETE USING (
        user_id = (current_setting('request.jwt.claims', true)::json ->> 'user_id')::int
    );

-- Grant permissions
GRANT ALL ON public.ml_stores TO anon;
GRANT ALL ON public.ml_stores TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE ml_stores_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE ml_stores_id_seq TO authenticated;

-- Comments for documentation
COMMENT ON TABLE public.ml_stores IS 'Multi-tenant MercadoLibre store connections with OAuth tokens';
COMMENT ON COLUMN public.ml_stores.app_secret_encrypted IS 'ML App Secret encrypted with application key';
COMMENT ON COLUMN public.ml_stores.state_token IS 'CSRF protection token for OAuth flow';
COMMENT ON COLUMN public.ml_stores.status IS 'Connection status: pending_authorization, connected, disconnected, error, expired';

-- Example usage queries (for testing)
/*
-- Get all stores for a user
SELECT id, nickname, site_id, status, connected_at 
FROM ml_stores 
WHERE user_id = 1;

-- Get connected stores only
SELECT * FROM ml_stores 
WHERE user_id = 1 AND status = 'connected';

-- Check if user has a store for specific site
SELECT EXISTS(
    SELECT 1 FROM ml_stores 
    WHERE user_id = 1 AND site_id = 'MLC' AND status = 'connected'
);
*/