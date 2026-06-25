# Backend Schema Design
## SmartSearch API — Semantic Search for E-commerce

**Version:** 1.0  
**Date:** 2026-06-22  
**Status:** Draft  
**Author:** Engineering Team

---

## 1. Database Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER ARCHITECTURE                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  PostgreSQL  │  │   ChromaDB   │  │      Redis Cache     │  │
│  │  (Primary)   │  │  (Vector)    │  │   (Session + Queue)  │  │
│  │              │  │              │  │                      │  │
│  │ • Users      │  │ • Product    │  │ • Sessions           │  │
│  │ • Stores     │  │   embeddings │  │ • Rate limits        │  │
│  │ • Products   │  │ • Search     │  │ • Search cache       │  │
│  │ • API Keys   │  │   indices    │  │ • Job queues         │  │
│  │ • Subscriptions│  │ • Query vectors│  │ • Real-time stats  │  │
│  │ • Audit Logs │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  ClickHouse  │  │    MinIO     │  │   Elasticsearch      │  │
│  │  (Analytics) │  │  (File Store)│  │   (Full-Text Fallback)│  │
│  │              │  │              │  │                      │  │
│  │ • Search logs│  │ • CSV uploads│  │ • Keyword backup     │  │
│  │ • Clickstream│  │ • Images     │  │ • Spell-check        │  │
│  │ • Conversion │  │ • Exports    │  │ • Fuzzy matching     │  │
│  │   funnel     │  │ • Backups    │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PostgreSQL Schema (Relational Data)

### 2.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),

    -- Status & Verification
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,

    -- Role & Permissions
    role VARCHAR(50) DEFAULT 'user', -- 'user', 'admin', 'super_admin'
    permissions JSONB DEFAULT '[]', -- ['stores:read', 'stores:write', 'analytics:read']

    -- Subscription
    current_tier VARCHAR(50) DEFAULT 'free', -- 'free', 'starter', 'pro', 'enterprise'
    subscription_status VARCHAR(50) DEFAULT 'active', -- 'active', 'past_due', 'cancelled', 'trialing'
    trial_ends_at TIMESTAMP,

    -- Stripe Integration
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    stripe_payment_method_id VARCHAR(255),

    -- Preferences
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB DEFAULT '{
        "email_weekly_report": true,
        "email_usage_alerts": true,
        "email_product_updates": false
    }',

    -- Metadata
    last_login_at TIMESTAMP,
    last_login_ip INET,
    login_count INTEGER DEFAULT 0,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_ip INET,

    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX idx_users_tier ON users(current_tier);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

### 2.2 Stores Table (Merchant Accounts)
```sql
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE, -- URL-friendly identifier
    description TEXT,

    -- Platform Integration
    platform VARCHAR(50) NOT NULL, -- 'shopify', 'woocommerce', 'bigcommerce', 'custom', 'csv'
    platform_store_id VARCHAR(255), -- External ID from platform
    platform_domain VARCHAR(255), -- e.g., "sarahs-jewelry.myshopify.com"
    custom_domain VARCHAR(255), -- CNAME pointing to us

    -- API & Webhooks
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255), -- HMAC secret for verification
    api_endpoint VARCHAR(500), -- For custom platform integrations
    api_key_encrypted TEXT, -- Encrypted API key for platform

    -- Sync Configuration
    sync_frequency VARCHAR(50) DEFAULT 'daily', -- 'realtime', 'hourly', 'daily', 'manual'
    sync_schedule JSONB DEFAULT '{"hour": 2, "minute": 0, "timezone": "UTC"}', -- For scheduled sync
    last_sync_at TIMESTAMP,
    last_sync_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'success', 'partial', 'failed'
    last_sync_error TEXT,
    next_sync_at TIMESTAMP,

    -- Index Status
    index_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'indexing', 'ready', 'error', 'paused'
    index_progress_percent INTEGER DEFAULT 0,
    index_started_at TIMESTAMP,
    index_completed_at TIMESTAMP,
    indexed_product_count INTEGER DEFAULT 0,
    total_product_count INTEGER DEFAULT 0,

    -- Widget Configuration
    widget_config JSONB DEFAULT '{
        "theme": "light",
        "primary_color": "#4F46E5",
        "position": "bottom-right",
        "placeholder_text": "Search for products...",
        "show_filters": true,
        "show_price": true,
        "show_rating": true,
        "results_per_page": 10,
        "enable_autocomplete": true,
        "enable_voice_search": false
    }',

    -- Search Settings
    search_config JSONB DEFAULT '{
        "min_score_threshold": 0.25,
        "max_results": 50,
        "enable_synonyms": true,
        "enable_spell_check": true,
        "fallback_to_keyword": true,
        "boost_recent": false,
        "boost_popular": false
    }',

    -- Usage Tracking (denormalized for fast queries)
    total_searches_all_time BIGINT DEFAULT 0,
    total_searches_this_month INTEGER DEFAULT 0,
    total_products INTEGER DEFAULT 0,

    -- Billing
    current_plan_id UUID REFERENCES subscription_plans(id),
    billing_cycle_start TIMESTAMP,
    billing_cycle_end TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_paused BOOLEAN DEFAULT FALSE,
    pause_reason VARCHAR(255),

    -- Metadata
    metadata JSONB DEFAULT '{}', -- Flexible store-specific data
    tags TEXT[], -- For internal organization

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP, -- Soft delete

    -- Constraints
    CONSTRAINT valid_platform CHECK (platform IN ('shopify', 'woocommerce', 'bigcommerce', 'custom', 'csv', 'api')),
    CONSTRAINT valid_sync_frequency CHECK (sync_frequency IN ('realtime', 'hourly', 'daily', 'manual'))
);

-- Indexes
CREATE INDEX idx_stores_user ON stores(user_id);
CREATE INDEX idx_stores_platform ON stores(platform);
CREATE INDEX idx_stores_status ON stores(index_status);
CREATE INDEX idx_stores_active ON stores(is_active) WHERE is_active = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_stores_slug ON stores(slug);
CREATE INDEX idx_stores_domain ON stores(platform_domain);
CREATE INDEX idx_stores_sync ON stores(sync_frequency, next_sync_at) WHERE is_active = TRUE;
```

### 2.3 Products Table (Metadata Cache)
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,

    -- External Reference
    external_id VARCHAR(255) NOT NULL, -- Platform's product ID
    variant_id VARCHAR(255), -- For variant-level products

    -- Core Content
    title VARCHAR(500) NOT NULL,
    description TEXT,
    short_description VARCHAR(1000),

    -- Categorization
    category VARCHAR(255),
    category_id VARCHAR(255),
    subcategories TEXT[],
    tags TEXT[],
    brand VARCHAR(255),

    -- Pricing
    price DECIMAL(10,2) NOT NULL,
    compare_at_price DECIMAL(10,2), -- Original price for sales
    currency VARCHAR(3) DEFAULT 'USD',
    cost_per_item DECIMAL(10,2), -- For margin calculations

    -- Inventory
    inventory_count INTEGER DEFAULT 0,
    inventory_policy VARCHAR(50) DEFAULT 'deny', -- 'deny', 'continue'
    sku VARCHAR(255),
    barcode VARCHAR(255),
    weight DECIMAL(8,2), -- In grams
    weight_unit VARCHAR(10) DEFAULT 'g',

    -- Media
    image_url VARCHAR(500),
    image_urls TEXT[], -- Gallery images
    video_url VARCHAR(500),

    -- Attributes (flexible schema)
    attributes JSONB DEFAULT '{}', -- {"color": "black", "material": "mesh", "size": "large"}

    -- Search & Discovery
    search_keywords TEXT[], -- Manually curated keywords
    search_boost_score DECIMAL(3,2) DEFAULT 1.00, -- Manual ranking boost
    is_featured BOOLEAN DEFAULT FALSE,
    is_searchable BOOLEAN DEFAULT TRUE,

    -- Status
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'draft', 'archived'
    availability VARCHAR(50) DEFAULT 'in_stock', -- 'in_stock', 'out_of_stock', 'preorder'

    -- Indexing Status
    index_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'indexed', 'failed', 'stale'
    last_indexed_at TIMESTAMP,
    index_error TEXT,
    embedding_version VARCHAR(50), -- Track which model version was used

    -- Metadata
    metadata JSONB DEFAULT '{}', -- Platform-specific data

    -- SEO
    seo_title VARCHAR(255),
    seo_description VARCHAR(500),
    url_handle VARCHAR(255), -- SEO-friendly URL

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP, -- When last synced from platform
    deleted_at TIMESTAMP, -- Soft delete

    -- Constraints
    CONSTRAINT unique_store_external UNIQUE(store_id, external_id),
    CONSTRAINT valid_status CHECK (status IN ('active', 'draft', 'archived')),
    CONSTRAINT valid_availability CHECK (availability IN ('in_stock', 'out_of_stock', 'preorder', 'backorder'))
);

-- Indexes
CREATE INDEX idx_products_store ON products(store_id);
CREATE INDEX idx_products_external ON products(store_id, external_id);
CREATE INDEX idx_products_status ON products(status) WHERE status = 'active';
CREATE INDEX idx_products_index ON products(index_status);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_featured ON products(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_products_searchable ON products(is_searchable) WHERE is_searchable = TRUE;

-- Full-text search index (for keyword fallback)
CREATE INDEX idx_products_fts ON products USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- GIN index for JSONB attributes
CREATE INDEX idx_products_attributes ON products USING gin(attributes);
```

### 2.4 API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE, -- NULL for global keys

    -- Key Data
    name VARCHAR(255) NOT NULL, -- e.g., "Production API", "Test Environment"
    key_prefix VARCHAR(10) NOT NULL, -- e.g., "ss_live_", "ss_test_"
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- bcrypt hash of full key
    key_last_four VARCHAR(4), -- Last 4 chars for display (like credit cards)

    -- Permissions
    permissions JSONB DEFAULT '["search"]', -- ['search', 'ingest', 'analytics', 'admin']

    -- Rate Limiting
    rate_limit_per_minute INTEGER DEFAULT 100,
    rate_limit_per_hour INTEGER DEFAULT 1000,
    rate_limit_per_day INTEGER DEFAULT 10000,

    -- Usage Tracking
    total_requests BIGINT DEFAULT 0,
    requests_this_month INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    revoked_at TIMESTAMP,
    revoked_reason TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by_ip INET,

    -- Constraints
    CONSTRAINT valid_prefix CHECK (key_prefix IN ('ss_live_', 'ss_test_'))
);

-- Indexes
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_store ON api_keys(store_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
```

### 2.5 Subscription Plans Table
```sql
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Plan Info
    name VARCHAR(50) NOT NULL UNIQUE, -- 'free', 'starter', 'pro', 'enterprise'
    display_name VARCHAR(255) NOT NULL, -- e.g., "Starter"
    description TEXT,

    -- Pricing
    price_monthly DECIMAL(10,2) NOT NULL,
    price_annually DECIMAL(10,2), -- NULL if no annual discount
    currency VARCHAR(3) DEFAULT 'USD',

    -- Limits
    product_limit INTEGER NOT NULL, -- 0 = unlimited
    search_limit_monthly INTEGER NOT NULL, -- 0 = unlimited
    store_limit INTEGER DEFAULT 1, -- Number of stores allowed
    team_member_limit INTEGER DEFAULT 1,

    -- Features (JSONB for flexibility)
    features JSONB DEFAULT '{
        "semantic_search": true,
        "keyword_fallback": true,
        "autocomplete": true,
        "analytics_basic": true,
        "analytics_advanced": false,
        "visual_search": false,
        "multi_language": false,
        "a_b_testing": false,
        "white_label": false,
        "api_access": true,
        "webhook_sync": true,
        "scheduled_sync": false,
        "priority_support": false,
        "dedicated_infrastructure": false,
        "custom_model": false,
        "sla": false
    }',

    -- Stripe
    stripe_price_id_monthly VARCHAR(255),
    stripe_price_id_annually VARCHAR(255),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE, -- Show on pricing page?
    sort_order INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Seed data
INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_annually, product_limit, search_limit_monthly, features) VALUES
('free', 'Free', 'For small stores testing semantic search', 0, NULL, 1000, 1000, 
 '{"semantic_search": true, "keyword_fallback": true, "autocomplete": true, "analytics_basic": true, "api_access": false, "webhook_sync": false, "scheduled_sync": false}'),
('starter', 'Starter', 'For growing stores ready to convert more', 29, 290, 5000, 10000, 
 '{"semantic_search": true, "keyword_fallback": true, "autocomplete": true, "analytics_basic": true, "analytics_advanced": false, "api_access": true, "webhook_sync": true, "scheduled_sync": true}'),
('pro', 'Pro', 'For serious stores with high search volume', 79, 790, 50000, 100000, 
 '{"semantic_search": true, "keyword_fallback": true, "autocomplete": true, "analytics_basic": true, "analytics_advanced": true, "visual_search": true, "multi_language": true, "a_b_testing": true, "api_access": true, "webhook_sync": true, "scheduled_sync": true, "priority_support": true}'),
('enterprise', 'Enterprise', 'Custom solutions for large operations', 299, NULL, 0, 0, 
 '{"semantic_search": true, "keyword_fallback": true, "autocomplete": true, "analytics_basic": true, "analytics_advanced": true, "visual_search": true, "multi_language": true, "a_b_testing": true, "white_label": true, "api_access": true, "webhook_sync": true, "scheduled_sync": true, "priority_support": true, "dedicated_infrastructure": true, "custom_model": true, "sla": true}');
```

### 2.6 Search Query Logs (Summary Table)
```sql
CREATE TABLE search_logs_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Aggregated Metrics
    total_queries INTEGER DEFAULT 0,
    unique_queries INTEGER DEFAULT 0,
    no_results_queries INTEGER DEFAULT 0,
    avg_latency_ms INTEGER,
    max_latency_ms INTEGER,
    p95_latency_ms INTEGER,
    p99_latency_ms INTEGER,

    -- Result Metrics
    avg_results_per_query DECIMAL(5,2),
    total_clicks INTEGER DEFAULT 0,
    total_add_to_carts INTEGER DEFAULT 0,
    total_purchases INTEGER DEFAULT 0,

    -- Conversion
    click_through_rate DECIMAL(5,4),
    add_to_cart_rate DECIMAL(5,4),
    purchase_rate DECIMAL(5,4),

    -- Top Data (JSONB for flexibility)
    top_queries JSONB DEFAULT '[]', -- [{"query": "ergonomic chair", "count": 42, "ctr": 0.45}]
    no_results_queries_list JSONB DEFAULT '[]',
    top_clicked_products JSONB DEFAULT '[]',

    -- Revenue Attribution
    attributed_revenue DECIMAL(12,2) DEFAULT 0,
    attributed_orders INTEGER DEFAULT 0,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_store_date UNIQUE(store_id, date)
);

-- Indexes
CREATE INDEX idx_search_logs_store ON search_logs_daily(store_id);
CREATE INDEX idx_search_logs_date ON search_logs_daily(date);
CREATE INDEX idx_search_logs_store_date ON search_logs_daily(store_id, date);
```

### 2.7 Webhook Events Table
```sql
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,

    -- Event Data
    event_type VARCHAR(100) NOT NULL, -- 'product.created', 'product.updated', 'product.deleted', 'order.placed'
    source VARCHAR(50) NOT NULL, -- 'shopify', 'woocommerce', 'manual', 'api'
    external_id VARCHAR(255), -- Platform's event ID

    -- Payload
    payload JSONB NOT NULL,
    payload_hash VARCHAR(64), -- SHA-256 for deduplication

    -- Processing
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'skipped'
    processed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,

    -- Audit
    received_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_event_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped'))
);

-- Indexes
CREATE INDEX idx_webhook_events_store ON webhook_events(store_id);
CREATE INDEX idx_webhook_events_status ON webhook_events(status) WHERE status IN ('pending', 'failed');
CREATE INDEX idx_webhook_events_type ON webhook_events(event_type);
CREATE INDEX idx_webhook_events_retry ON webhook_events(next_retry_at) WHERE status = 'failed';
```

### 2.8 Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Actor
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    actor_type VARCHAR(50) NOT NULL, -- 'user', 'api_key', 'system', 'webhook'
    actor_ip INET,
    actor_user_agent TEXT,

    -- Action
    action VARCHAR(100) NOT NULL, -- 'store.created', 'product.updated', 'search.performed', 'api_key.revoked'
    resource_type VARCHAR(50) NOT NULL, -- 'store', 'product', 'user', 'api_key', 'search'
    resource_id UUID, -- ID of affected resource

    -- Details
    before_state JSONB, -- Previous state (for updates)
    after_state JSONB, -- New state
    changes_summary JSONB, -- Computed diff

    -- Context
    request_id VARCHAR(255), -- For tracing
    request_path VARCHAR(500),
    request_method VARCHAR(10),
    response_status INTEGER,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

---

## 3. ChromaDB Schema (Vector Store)

### 3.1 Collection Structure
```python
# One collection per store for data isolation
COLLECTION_NAME_TEMPLATE = "products_store_{store_id}"

COLLECTION_METADATA = {
    "store_id": "uuid-string",
    "hnsw:space": "cosine",           # Distance metric
    "hnsw:construction_ef": 128,      # Build-time accuracy/speed tradeoff
    "hnsw:search_ef": 64,             # Query-time accuracy/speed tradeoff
    "hnsw:M": 16,                     # Max edges per node
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "chunk_size": 500,
    "chunk_overlap": 100,
    "created_at": "2026-06-22T10:00:00Z",
    "version": "1.0"
}

# Document (Chunk) Structure
DOCUMENT = {
    "id": "product_uuid_chunk_0",           # Unique chunk ID
    "document": "chunk text content",         # The actual text chunk
    "embedding": [0.023, -0.156, ...],       # 384-dim float vector
    "metadata": {
        # Product Reference
        "product_id": "product_uuid",
        "external_id": "shopify_123456789",
        "store_id": "store_uuid",

        # Content
        "title": "Product Title",
        "chunk_index": 0,                    # Which chunk this is
        "total_chunks": 3,                   # Total chunks for this product
        "chunk_type": "description",         # 'title', 'description', 'tags', 'attributes'

        # Searchable Attributes
        "price": 199.99,
        "currency": "USD",
        "category": "office-furniture",
        "subcategories": ["chairs", "ergonomic"],
        "brand": "ErgoTech",
        "tags": ["ergonomic", "office", "chair"],

        # Status
        "is_active": True,
        "is_searchable": True,
        "availability": "in_stock",

        # Media
        "image_url": "https://cdn.store.com/image.jpg",

        # Ranking Signals
        "boost_score": 1.0,
        "popularity_score": 0.85,          # Derived from clicks/purchases
        "recency_score": 0.92,             # How recently added

        # Indexing
        "indexed_at": "2026-06-22T10:00:00Z",
        "embedding_version": "all-MiniLM-L6-v2-v1.0"
    }
}
```

### 3.2 Indexing Strategy
```python
# Chunking Strategy
CHUNK_CONFIG = {
    "title": {
        "chunk_size": 500,      # Full title (usually short)
        "chunk_overlap": 0,
        "priority": 1.5         # Boost title matches
    },
    "description": {
        "chunk_size": 500,
        "chunk_overlap": 100,
        "priority": 1.0
    },
    "tags": {
        "chunk_size": 500,      # All tags concatenated
        "chunk_overlap": 0,
        "priority": 1.2
    },
    "attributes": {
        "chunk_size": 500,      # Key-value pairs as text
        "chunk_overlap": 0,
        "priority": 0.8
    }
}

# HNSW Index Parameters (for ChromaDB)
HNSW_CONFIG = {
    "M": 16,                    # Max edges per node (higher = more accurate, slower)
    "ef_construction": 128,     # Build-time search depth
    "ef_search": 64,            # Query-time search depth
    "space": "cosine"           # Distance metric: cosine, l2, ip
}

# Search Parameters
SEARCH_CONFIG = {
    "n_results": 50,            # Max results to retrieve
    "min_score": 0.25,          # Minimum similarity score (0-1)
    "rerank_top_k": 20,         # Top K to rerank with cross-encoder
    "final_results": 10         # Results returned to user
}
```

---

## 4. Redis Schema (Cache & Queue)

### 4.1 Key Patterns
```redis
# Session Management (JWT blacklist + active sessions)
session:{jwt_token_hash} → {
    "user_id": "uuid",
    "store_ids": ["uuid1", "uuid2"],
    "permissions": ["search", "ingest"],
    "created_at": "timestamp",
    "expires_at": "timestamp"
} TTL: 24h

# Rate Limiting (Token Bucket)
rate_limit:{api_key_id}:{minute_bucket} → 42  (counter) TTL: 60s
rate_limit:{api_key_id}:{hour_bucket} → 342  (counter) TTL: 3600s
rate_limit:{api_key_id}:{day_bucket} → 4521  (counter) TTL: 86400s

# Search Result Cache
search_cache:{store_id}:{query_hash}:{filters_hash}:{page} → {
    "results": [...],
    "total": 47,
    "cached_at": "timestamp"
} TTL: 300s (5 min)

# Autocomplete Cache
autocomplete:{store_id}:{prefix_hash} → {
    "suggestions": ["query1", "query2", ...],
    "cached_at": "timestamp"
} TTL: 3600s (1 hour)

# Index Status
index_status:{store_id} → {
    "status": "indexing",
    "progress": 65,
    "total_products": 487,
    "indexed_products": 317,
    "started_at": "timestamp",
    "estimated_completion": "timestamp"
} TTL: 3600s

# Store Configuration Cache
store_config:{store_id} → {
    "widget_config": {...},
    "search_config": {...},
    "plan_features": {...}
} TTL: 3600s

# Real-time Stats (Sliding Window)
stats:searches:{store_id}:{hour_bucket} → 1247  (counter) TTL: 7200s
stats:latency:{store_id}:{hour_bucket} → [142, 156, 138, ...]  (list, trimmed to 1000) TTL: 7200s

# Job Queue (Celery)
celery:queue:ingestion → [job_id1, job_id2, ...]
celery:queue:sync → [job_id1, job_id2, ...]
celery:queue:analytics → [job_id1, job_id2, ...]

# Job Status
job:{job_id} → {
    "status": "processing",
    "progress": 45,
    "total": 487,
    "completed": 219,
    "errors": 3,
    "started_at": "timestamp",
    "updated_at": "timestamp"
} TTL: 86400s
```

### 4.2 Pub/Sub Channels
```redis
# Real-time notifications
channel:store:{store_id}:index_complete → "Index complete: 487 products"
channel:store:{store_id}:sync_error → "Sync failed: invalid API key"
channel:user:{user_id}:billing_alert → "Approaching search limit"

# WebSocket-like updates for dashboard
channel:store:{store_id}:search_spike → {"queries_per_min": 245, "threshold": 200}
```

---

## 5. ClickHouse Schema (Analytics)

### 5.1 Search Queries Table
```sql
CREATE TABLE search_queries (
    -- Time & Identity
    timestamp DateTime64(3),           -- Millisecond precision
    query_id UUID,
    store_id UUID,

    -- Query Details
    query String,                       -- Raw query text
    query_normalized String,            -- Lowercase, stemmed, stopwords removed
    query_length UInt8,                 -- Character count
    query_word_count UInt8,             -- Word count

    -- User Context
    user_id Nullable(UUID),             -- NULL for anonymous widget users
    session_id UUID,
    source String,                      -- 'api', 'widget', 'dashboard', 'mobile_app'

    -- Search Parameters
    filters_used JSON,                  -- {"price_max": 200, "category": "chairs"}
    n_results_requested UInt8,

    -- Results
    results_count UInt32,
    results_returned UInt8,
    latency_ms UInt32,

    -- Engagement (filled async via pixel/events)
    clicked_results Array(UUID),        -- Product IDs clicked
    click_positions Array(UInt8),       -- Positions in results (1-indexed)
    added_to_cart Array(UUID),
    purchased Array(UUID),

    -- Revenue Attribution
    attributed_revenue Decimal(12,2),
    attributed_orders UInt8,

    -- Metadata
    is_no_results UInt8,                -- 1 if results_count == 0
    is_autocomplete UInt8,              -- 1 if from autocomplete selection
    is_voice_search UInt8,              -- 1 if voice input

    -- Request Context
    request_id String,
    api_key_id Nullable(UUID),
    ip_address IPv4,
    user_agent String,
    country String,                     -- GeoIP
    device_type String,                 -- 'desktop', 'mobile', 'tablet'

    -- Insert time
    inserted_at DateTime64(3) DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (store_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;       -- Auto-delete after 2 years

-- Materialized Views for Aggregations
CREATE MATERIALIZED VIEW search_queries_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (store_id, hour)
AS SELECT
    toStartOfHour(timestamp) as hour,
    store_id,
    count() as total_queries,
    uniq(query_normalized) as unique_queries,
    sum(is_no_results) as no_results_queries,
    avg(latency_ms) as avg_latency_ms,
    quantile(0.95)(latency_ms) as p95_latency_ms,
    avg(results_count) as avg_results_count,
    sum(length(clicked_results)) as total_clicks,
    sum(length(added_to_cart)) as total_add_to_carts,
    sum(length(purchased)) as total_purchases,
    sum(attributed_revenue) as total_revenue
FROM search_queries
GROUP BY hour, store_id;
```

### 5.2 Product Events Table
```sql
CREATE TABLE product_events (
    timestamp DateTime64(3),
    store_id UUID,
    product_id UUID,

    event_type String,                 -- 'search_appear', 'click', 'cart_add', 'purchase', 'view'
    query_id Nullable(UUID),            -- NULL if not from search

    -- Search Context
    search_position UInt8,              -- Position in search results (0 if not from search)
    search_score Float32,              -- Semantic similarity score

    -- Revenue
    revenue Nullable(Decimal(12,2)),    -- For purchase events
    quantity Nullable(UInt8),

    -- User
    session_id UUID,
    user_id Nullable(UUID),

    -- Context
    request_id String,
    ip_address IPv4,
    user_agent String,

    inserted_at DateTime64(3) DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (store_id, product_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;
```

---

## 6. MinIO/S3 Schema (File Storage)

### 6.1 Bucket Structure
```
smartsearch-uploads/
├── stores/
│   ├── {store_id}/
│   │   ├── imports/
│   │   │   ├── 2026-06-22/
│   │   │   │   ├── products_20260622_143022.csv
│   │   │   │   └── products_20260622_143022_result.json
│   │   ├── exports/
│   │   │   └── analytics_2026-05-01_2026-05-31.csv
│   │   └── images/
│   │       └── product_thumbnails/
│   └── templates/
│       └── import_template.csv
├── backups/
│   ├── chromadb/
│   │   └── daily/
│   │       └── chroma_backup_2026-06-22.tar.gz
│   └── postgres/
│       └── daily/
│           └── pg_dump_2026-06-22.sql.gz
└── public/
    └── widget/
        └── v1.2.3/
            ├── widget.js
            ├── widget.css
            └── widget.min.js
```

### 6.2 Object Metadata
```json
{
    "store_id": "uuid",
    "uploaded_by": "user_uuid",
    "uploaded_at": "2026-06-22T14:30:22Z",
    "file_type": "csv",
    "row_count": 487,
    "processing_status": "completed",
    "processing_duration_ms": 12450,
    "errors_count": 3,
    "checksum": "sha256:abc123..."
}
```

---

## 7. Data Flow & ETL

### 7.1 Product Sync Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCT SYNC ETL PIPELINE                                     │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   SOURCE     │    │   EXTRACT    │    │  TRANSFORM   │     │
│  │              │    │              │    │              │     │
│  │ Shopify API  │───▶│ REST/GraphQL │───▶│ Normalize    │     │
│  │ WooCommerce  │    │ Webhook      │    │ Validate     │     │
│  │ CSV Upload   │    │ CSV Parser   │    │ Enrich       │     │
│  │ Manual Entry │    │              │    │              │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                   │             │
│                                                   ▼             │
│                                          ┌──────────────┐     │
│                                          │   CHUNKING   │     │
│                                          │              │     │
│                                          │ • Title chunk│     │
│                                          │ • Desc chunks│     │
│                                          │ • Tags chunk │     │
│                                          │ • Attr chunks│     │
│                                          └──────┬───────┘     │
│                                                 │             │
│                                                 ▼             │
│                                          ┌──────────────┐     │
│                                          │  EMBEDDING   │     │
│                                          │              │     │
│                                          │ all-MiniLM   │     │
│                                          │ 384-dim      │     │
│                                          │ CPU batch    │     │
│                                          └──────┬───────┘     │
│                                                 │             │
│                                                 ▼             │
│                                          ┌──────────────┐     │
│                                          │    LOAD      │     │
│                                          │              │     │
│                                          │ PostgreSQL   │     │
│                                          │ ChromaDB     │     │
│                                          │ Redis cache  │     │
│                                          └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Search Query Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│  SEARCH QUERY PIPELINE                                           │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   QUERY      │    │  PREPROCESS  │    │   EMBED      │     │
│  │              │    │              │    │              │     │
│  │ "comfy chair│───▶│ • Lowercase  │───▶│ all-MiniLM   │     │
│  │  for work" │    │ • Spell check│    │ • 384-dim    │     │
│  │              │    │ • Synonyms   │    │ vector       │     │
│  │              │    │ • Stopwords  │    │              │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                   │             │
│                                                   ▼             │
│                                          ┌──────────────┐     │
│                                          │ VECTOR SEARCH│     │
│                                          │              │     │
│                                          │ ChromaDB     │     │
│                                          │ Cosine sim   │     │
│                                          │ Top 50       │     │
│                                          └──────┬───────┘     │
│                                                 │             │
│                                                 ▼             │
│                                          ┌──────────────┐     │
│                                          │  POST-PROC   │     │
│                                          │              │     │
│                                          │ • Filters    │     │
│                                          │ • Deduplicate│     │
│                                          │ • Re-rank    │     │
│                                          │ • Merge chunks│     │
│                                          └──────┬───────┘     │
│                                                 │             │
│                                                 ▼             │
│                                          ┌──────────────┐     │
│                                          │   RESPONSE   │     │
│                                          │              │     │
│                                          │ • JSON       │     │
│                                          │ • Cache      │     │
│                                          │ • Log        │     │
│                                          └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Data Retention & GDPR

### 8.1 Retention Policies
| Data Type | Retention | Action |
|-----------|-----------|--------|
| Search queries (raw) | 2 years | Auto-delete (ClickHouse TTL) |
| Search queries (aggregated) | 5 years | Archive to cold storage |
| Product embeddings | Until store deletion | Delete with store |
| API request logs | 90 days | Auto-delete |
| Audit logs | 7 years | Archive after 2 years |
| File uploads | 30 days post-processing | Auto-delete |
| Session data | 24 hours | Redis TTL |
| Search cache | 5 minutes | Redis TTL |

### 8.2 GDPR Compliance
```sql
-- Right to be forgotten (user deletion)
-- Cascades: users → stores → products → embeddings
-- Anonymizes: search_queries (replace user_id with NULL, scramble query)

-- Data export (user request)
-- Generates: JSON/CSV with all personal data
-- Includes: user profile, stores, products, search history, billing

-- Data processing agreement
-- Stored: in metadata JSONB for each store
-- Version tracked: in audit_logs
```

---

## 9. Backup & Disaster Recovery

### 9.1 Backup Strategy
| Component | Frequency | Method | Retention |
|-----------|-----------|--------|-----------|
| PostgreSQL | Daily | pg_dump + WAL archiving | 30 days |
| ChromaDB | Daily | Collection export + tar | 30 days |
| Redis | Hourly | RDB snapshot | 7 days |
| ClickHouse | Daily | FREEZE + copy parts | 90 days |
| MinIO | Continuous | Cross-region replication | 1 year |

### 9.2 Recovery Objectives
| Tier | RTO (Recovery Time) | RPO (Data Loss) |
|------|---------------------|-----------------|
| Free/Starter | 24 hours | 24 hours |
| Pro | 4 hours | 1 hour |
| Enterprise | 1 hour | 15 minutes |

---

*End of Backend Schema Design*
