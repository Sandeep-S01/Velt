# Technical Requirements Document (TRD)
## SmartSearch API — Semantic Search for E-commerce

**Version:** 1.0  
**Date:** 2026-06-22  
**Status:** Draft  
**Author:** Technical Team

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  JS Widget  │  │  Dashboard  │  │  REST API Clients   │  │
│  │  (Browser)  │  │  (React SPA)│  │  (cURL, Postman)    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Nginx     │  │  Rate Limiter│  │   Auth Middleware   │  │
│  │  (Reverse   │  │  (Redis)    │  │  (JWT + API Keys)   │  │
│  │   Proxy)    │  │             │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Search     │  │  Ingestion  │  │   Analytics Engine  │  │
│  │  Service    │  │  Service    │  │   (Query logging)   │  │
│  │  (FastAPI)  │  │  (FastAPI)  │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Webhook    │  │  Sync       │  │   Auth Service      │  │
│  │  Handler    │  │  Scheduler  │  │   (User/Store mgmt) │  │
│  │  (FastAPI)  │  │  (Celery)   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  ChromaDB   │  │  PostgreSQL │  │   Redis Cache       │  │
│  │  (Vector    │  │  (Relational│  │   (Session + Rate   │  │
│  │   Store)    │  │   Data)     │  │    Limit + Queue)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │  S3/MinIO   │  │  ClickHouse │                          │
│  │  (File      │  │  (Analytics │                          │
│  │   Storage)  │  │   Logs)     │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### 2.1 Backend Framework
| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **API Framework** | FastAPI | 0.110+ | Async-native, auto-docs, Pydantic validation, Python ecosystem |
| **ASGI Server** | Uvicorn | 0.27+ | High-performance async server, HTTP/2 support |
| **Task Queue** | Celery + Redis | 5.3+ | Background jobs (sync, indexing, emails), battle-tested |
| **Scheduler** | Celery Beat | 5.3+ | Periodic sync jobs, cleanup tasks |
| **Process Manager** | Gunicorn | 21.2+ | Worker process management, graceful restarts |

### 2.2 AI/ML Layer
| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Embedding Model** | sentence-transformers | 2.5+ | `all-MiniLM-L6-v2` (80MB, CPU-optimized, 384-dim) |
| **Alternative Model** | `BAAI/bge-small-en-v1.5` | latest | Better quality, slightly slower, 512-dim |
| **Vector DB** | ChromaDB | 0.4+ | Persistent local storage, zero-config, Python-native |
| **Future Scale** | Qdrant | 1.8+ | If we need >1M vectors, distributed, HNSW indexing |
| **Text Processing** | spaCy | 3.7+ | Tokenization, entity extraction, query preprocessing |
| **Chunking** | LangChain | 0.1+ | Document chunking strategies, overlap management |

### 2.3 Data Storage
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Primary DB** | PostgreSQL | 16+ | Users, stores, products metadata, subscriptions |
| **Vector Store** | ChromaDB | 0.4+ | Product embeddings, semantic search index |
| **Cache** | Redis | 7.2+ | Session store, rate limiting, search result cache |
| **Analytics** | ClickHouse | 24+ | Query logs, search metrics, time-series data |
| **File Storage** | MinIO (S3-compatible) | latest | Product images, CSV uploads, export files |
| **Search Cache** | Redis (JSON) | 7.2+ | Hot query results, autocomplete suggestions |

### 2.4 Frontend
| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Dashboard** | React + TypeScript | 18+ | Component ecosystem, type safety |
| **UI Framework** | Tailwind CSS | 3.4+ | Utility-first, rapid development, consistent design |
| **State Management** | Zustand | 4.5+ | Lightweight, no boilerplate vs Redux |
| **Charts** | Recharts | 2.12+ | React-native charts, responsive |
| **JS Widget** | Vanilla JS | ES6+ | Zero dependencies, < 50KB, maximum compatibility |
| **Widget Build** | Vite | 5.0+ | Fast bundling, tree-shaking, small output |

### 2.5 DevOps & Infrastructure
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Containerization** | Docker + Docker Compose | 25+ | Local dev, deployment consistency |
| **Orchestration** | Docker Swarm (MVP) | latest | Simple container orchestration |
| **Future Scale** | Kubernetes | 1.29+ | If we need auto-scaling, multi-region |
| **Reverse Proxy** | Nginx | 1.25+ | SSL termination, load balancing, static files |
| **CI/CD** | GitHub Actions | latest | Test, build, deploy automation |
| **Monitoring** | Prometheus + Grafana | latest | Metrics, alerts, dashboards |
| **Logging** | Loki + Grafana | latest | Centralized log aggregation |
| **Error Tracking** | Sentry | latest | Exception tracking, performance monitoring |

### 2.6 External APIs & Integrations
| Service | Purpose | Auth | Rate Limits |
|---------|---------|------|-------------|
| **Shopify API** | Product sync, webhooks | OAuth 2.0 | 2 req/sec (REST), 10 req/sec (GraphQL) |
| **WooCommerce API** | Product sync | API Key | Configurable by store |
| **BigCommerce API** | Product sync (Phase 2) | OAuth 2.0 | 400 req/sec |
| **Stripe API** | Payments, subscriptions | API Key | 100 req/sec |
| **SendGrid/Mailgun** | Transactional emails | API Key | 1000 emails/day (free tier) |
| **Sentry API** | Error reporting | DSN | 5000 events/day (free tier) |

---

## 3. API Specifications

### 3.1 Authentication
**Method:** API Key (X-API-Key header) + JWT for dashboard sessions  
**Registration:** Email + password, or OAuth (Google, GitHub)  
**API Key Format:** `ss_live_xxxxxxxxxxxxxxxx` (live) / `ss_test_xxxxxxxxxxxxxxxx` (test)

### 3.2 Core Endpoints

#### POST /api/v1/search
**Description:** Semantic search across indexed products  
**Auth:** API Key  
**Rate Limit:** 100 req/min (Starter), 1000 req/min (Pro)

**Request Body:**
```json
{
  "query": "comfortable chair for long hours at desk",
  "store_id": "store_abc123",
  "filters": {
    "price_min": 50,
    "price_max": 300,
    "category": "furniture",
    "in_stock": true
  },
  "n_results": 10,
  "offset": 0
}
```

**Response (200):**
```json
{
  "query": "comfortable chair for long hours at desk",
  "results_count": 10,
  "total_matches": 47,
  "results": [
    {
      "product_id": "prod_789",
      "score": 0.89,
      "title": "Ergonomic Office Chair Pro",
      "description": "Lumbar support, breathable mesh, adjustable height...",
      "price": 199.99,
      "image_url": "https://cdn.store.com/chair.jpg",
      "url": "https://store.com/products/chair-pro",
      "metadata": {
        "category": "office-furniture",
        "brand": "ErgoTech",
        "rating": 4.7
      },
      "matched_chunk": "...lumbar support and breathable mesh back perfect for long work sessions..."
    }
  ],
  "latency_ms": 142,
  "suggestions": ["ergonomic chair", "standing desk", "foot rest"]
}
```

#### POST /api/v1/ingest
**Description:** Add or update products in index  
**Auth:** API Key  
**Rate Limit:** 10 req/min

**Request Body:**
```json
{
  "store_id": "store_abc123",
  "products": [
    {
      "id": "prod_789",
      "title": "Ergonomic Office Chair Pro",
      "description": "Full description text...",
      "price": 199.99,
      "category": "office-furniture",
      "tags": ["ergonomic", "office", "chair"],
      "image_url": "https://...",
      "inventory_count": 15,
      "metadata": {
        "brand": "ErgoTech",
        "color": "black",
        "material": "mesh"
      }
    }
  ],
  "sync_mode": "upsert"
}
```

**Response (202):**
```json
{
  "job_id": "job_xyz789",
  "status": "queued",
  "estimated_completion": "30 seconds",
  "products_received": 1,
  "check_status_url": "/api/v1/jobs/job_xyz789"
}
```

#### GET /api/v1/stores/{store_id}/stats
**Description:** Search analytics for a store  
**Auth:** API Key + Store ownership

**Response (200):**
```json
{
  "store_id": "store_abc123",
  "period": "last_30_days",
  "total_searches": 15420,
  "unique_queries": 3847,
  "no_results_rate": 0.08,
  "avg_results_per_query": 12.4,
  "top_queries": [
    {"query": "ergonomic chair", "count": 342, "ctr": 0.45},
    {"query": "standing desk", "count": 287, "ctr": 0.38}
  ],
  "no_results_queries": [
    {"query": "purple bean bag", "count": 23, "suggestion": "Consider adding bean bag products"}
  ],
  "search_conversion_rate": 0.12
}
```

### 3.3 Webhook Endpoints

#### POST /webhooks/shopify/product_update
**Description:** Receive Shopify product webhooks for real-time sync  
**Auth:** HMAC signature verification  
**Processing:** Queue to Celery → fetch full product → re-embed → update index

#### POST /webhooks/shopify/product_delete
**Description:** Remove deleted products from index  
**Processing:** Immediate vector deletion + metadata cleanup

### 3.4 Widget Endpoints

#### GET /widget/v1/config?store_id=xxx
**Description:** Serve widget configuration (colors, layout, filters)  
**Response:** JSON config + CDN URL for widget JS

#### GET /widget/v1/search?query=xxx&store_id=xxx
**Description:** CORS-enabled search endpoint for JS widget  
**Response:** JSONP-compatible search results

---

## 4. Database Schema

### 4.1 PostgreSQL (Relational Data)

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255)
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    permissions JSONB DEFAULT '["search", "ingest"]',
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Stores (Merchant Accounts)
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'shopify', 'woocommerce', 'custom'
    platform_store_id VARCHAR(255),
    domain VARCHAR(255),
    webhook_url VARCHAR(500),
    sync_frequency VARCHAR(50) DEFAULT 'daily', -- 'realtime', 'hourly', 'daily', 'manual'
    last_sync_at TIMESTAMP,
    product_count INTEGER DEFAULT 0,
    index_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'indexing', 'ready', 'error'
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Products (Metadata Cache)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    compare_at_price DECIMAL(10,2),
    category VARCHAR(255),
    tags TEXT[],
    image_url VARCHAR(500),
    inventory_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_indexed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(store_id, external_id)
);

-- Subscription Plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_annually DECIMAL(10,2),
    product_limit INTEGER NOT NULL,
    search_limit_monthly INTEGER NOT NULL,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE
);

-- Search Query Logs (Summary, not raw - raw goes to ClickHouse)
CREATE TABLE search_logs_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_queries INTEGER DEFAULT 0,
    unique_queries INTEGER DEFAULT 0,
    no_results_queries INTEGER DEFAULT 0,
    avg_latency_ms INTEGER,
    top_queries JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(store_id, date)
);
```

### 4.2 ChromaDB (Vector Store)

**Collection Schema:**
```python
{
    "name": "products_store_{store_id}",  # One collection per store
    "metadata": {
        "store_id": "uuid",
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 128,
        "hnsw:search_ef": 64,
        "embedding_model": "all-MiniLM-L6-v2",
        "created_at": "timestamp"
    },
    "documents": ["chunk_text"],  # Product description chunks
    "embeddings": [[384-dim vector]],  # Sentence embeddings
    "metadatas": [{
        "product_id": "uuid",
        "external_id": "shopify_product_id",
        "title": "Product Title",
        "price": 199.99,
        "category": "office-furniture",
        "chunk_index": 0,
        "total_chunks": 3,
        "is_active": True
    }],
    "ids": ["product_id_chunk_0"]  # Unique chunk IDs
}
```

### 4.3 Redis (Cache & Queue)

**Key Patterns:**
```
# Session Cache
session:{jwt_token} → {user_id, store_ids, permissions}  (TTL: 24h)

# Rate Limiting
rate_limit:{api_key}:{minute_timestamp} → {count}  (TTL: 60s)

# Search Result Cache
search_cache:{store_id}:{query_hash}:{filters_hash} → {results_json}  (TTL: 300s)

# Autocomplete Cache
autocomplete:{store_id}:{prefix} → {suggestions_json}  (TTL: 3600s)

# Job Queue (Celery)
celery:queue:ingestion → [job_ids]
celery:queue:sync → [job_ids]

# Index Status
index_status:{store_id} → {status, progress_percent, last_updated}  (TTL: 3600s)
```

### 4.4 ClickHouse (Analytics)

```sql
CREATE TABLE search_queries (
    timestamp DateTime64(3),
    store_id UUID,
    query_id UUID,
    query String,
    query_normalized String,  -- Lowercase, stemmed, stopwords removed
    user_id UUID,  -- Nullable for widget searches
    session_id UUID,
    source String,  -- 'api', 'widget', 'dashboard'
    results_count UInt32,
    latency_ms UInt32,
    clicked_results Array(UUID),  -- Product IDs clicked
    added_to_cart Array(UUID),
    purchased Array(UUID),
    filters_used JSON,
    is_no_results UInt8  -- 1 if results_count == 0
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (store_id, timestamp);

CREATE TABLE product_events (
    timestamp DateTime64(3),
    store_id UUID,
    product_id UUID,
    event_type String,  -- 'view', 'search_appear', 'click', 'cart_add', 'purchase'
    query_id UUID,  -- Nullable if not from search
    position UInt32,  -- Position in search results
    revenue Decimal(10,2)  -- For purchase events
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (store_id, timestamp);
```

---

## 5. Data Flow Diagrams

### 5.1 Product Ingestion Flow
```
Merchant uploads CSV / Shopify webhook fires
         │
         ▼
┌─────────────────┐
│  Ingestion API  │ ← Validates format, auth, rate limits
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Celery Queue   │ ← Background job queued
│    (Redis)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ingest Worker  │ ← Parses CSV, chunks descriptions
│   (Python)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding Model │ ← all-MiniLM-L6-v2 generates 384-dim vectors
│  (CPU/GPU)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    ChromaDB     │ ← Vectors stored with metadata
│  (Persistent)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ ← Product metadata cached
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Webhook/Email  │ ← Notify merchant: "Index ready! 1,247 products"
│                 │
└─────────────────┘
```

### 5.2 Search Query Flow
```
Customer types query in store search bar
         │
         ▼
┌─────────────────┐
│   JS Widget     │ ← Captures input, debounce 300ms
│   (Browser)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Search API     │ ← Auth check, rate limit, input validation
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query Cache?   │ ← Redis check: exact query + filters cached?
│    (Redis)      │
└────────┬────────┘
    Yes / No
     │      │
     │      ▼
     │  ┌─────────────────┐
     │  │ Query Preprocess│ ← Lowercase, spell-check, synonym expansion
     │  │   (spaCy)       │
     │  └────────┬────────┘
     │           │
     │           ▼
     │  ┌─────────────────┐
     │  │ Embedding Model │ ← Generate query vector (same model as products)
     │  │  (all-MiniLM)   │
     │  └────────┬────────┘
     │           │
     │           ▼
     │  ┌─────────────────┐
     │  │  Vector Search  │ ← ChromaDB cosine similarity, top-K results
     │  │    (ChromaDB)   │
     │  └────────┬────────┘
     │           │
     │           ▼
     │  ┌─────────────────┐
     │  │  Post-Process   │ ← Apply filters (price, stock), re-rank, dedupe
     │  │   (Python)      │
     │  └────────┬────────┘
     │           │
     │           ▼
     │  ┌─────────────────┐
     │  │  Cache Results  │ ← Store in Redis (TTL: 5 min)
     │  │    (Redis)      │
     │  └────────┬────────┘
     │           │
     └───────────┤
                 ▼
        ┌─────────────────┐
        │  Log to ClickHouse│ ← Query, latency, results, clicks (async)
        │                 │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Response JSON  │ ← Return ranked products to widget
        │                 │
        └─────────────────┘
```

---

## 6. Performance Requirements

### 6.1 Search Latency Budget (P95)
| Component | Target | Max |
|-----------|--------|-----|
| Network (widget → API) | 50ms | 100ms |
| API processing | 30ms | 50ms |
| Cache lookup | 5ms | 10ms |
| Query embedding | 50ms | 100ms |
| Vector search (ChromaDB) | 30ms | 80ms |
| Post-processing | 20ms | 40ms |
| **Total** | **185ms** | **380ms** |

### 6.2 Throughput Targets
| Tier | Searches/Month | Peak QPS | Concurrent Users |
|------|----------------|----------|------------------|
| Free | 1,000 | 0.1 | 10 |
| Starter | 10,000 | 1 | 100 |
| Pro | 100,000 | 10 | 1,000 |
| Enterprise | Unlimited | 100+ | 10,000+ |

### 6.3 Indexing Performance
| Metric | Target |
|--------|--------|
| Products indexed per second | 50-100 (CPU) |
| Time to index 1,000 products | < 2 minutes |
| Time to index 50,000 products | < 2 hours |
| Real-time webhook processing | < 30 seconds |

---

## 7. Security Requirements

### 7.1 Authentication & Authorization
- **API Keys:** 32-byte random strings, hashed with bcrypt in DB, prefix indicates environment (`ss_live_` vs `ss_test_`)
- **JWT:** RS256 signed, 24h expiry, refresh token rotation
- **OAuth:** Shopify OAuth 2.0 for store connection, minimal scopes (`read_products`, `read_inventory`)
- **Permission Model:** Role-based (owner, admin, viewer) per store

### 7.2 Data Protection
- **Encryption at Rest:** PostgreSQL with AES-256, ChromaDB files on encrypted volumes
- **Encryption in Transit:** TLS 1.3 minimum, HSTS headers
- **PII Handling:** GDPR-compliant deletion, data processing agreement, EU data residency option
- **Webhook Verification:** HMAC-SHA256 signature validation for all Shopify webhooks

### 7.3 Rate Limiting
| Tier | Burst | Sustained |
|------|-------|-----------|
| Free | 5/min | 100/day |
| Starter | 20/min | 10,000/month |
| Pro | 100/min | 100,000/month |
| Enterprise | Custom | Custom |

**Enforcement:** Redis token bucket, 429 response with Retry-After header

---

## 8. Scalability Plan

### Phase 1: MVP (0-100 merchants)
- Single server: 4 vCPU, 8GB RAM
- Docker Compose on VPS (Hetzner/DigitalOcean: $40/month)
- ChromaDB persistent on SSD
- Daily backups to S3/MinIO

### Phase 2: Growth (100-1,000 merchants)
- Separate API and worker servers
- Redis cluster for cache + queue
- PostgreSQL read replica
- CDN for widget JS (CloudFlare)

### Phase 3: Scale (1,000+ merchants)
- Kubernetes cluster (3+ nodes)
- Qdrant vector cluster (distributed HNSW)
- ClickHouse cluster for analytics
- Multi-region deployment (US-East, EU-West, APAC)
- Auto-scaling based on search QPS

---

## 9. Monitoring & Alerting

### 9.1 Key Metrics
| Metric | Warning | Critical |
|--------|---------|----------|
| Search P95 latency | > 300ms | > 500ms |
| API error rate | > 1% | > 5% |
| Index queue depth | > 100 jobs | > 1000 jobs |
| DB connection pool | > 80% | > 95% |
| Disk usage | > 70% | > 90% |
| Memory usage | > 80% | > 95% |

### 9.2 Alert Channels
- PagerDuty (critical)
- Slack (warnings)
- Email (daily summaries)
- Sentry (error tracking)

---

## 10. Development Environment

### 10.1 Local Setup (Windows 10 Compatible)
```bash
# Prerequisites: Python 3.11+, Docker Desktop, Git

# Clone repo
git clone https://github.com/smartsearch/api.git
cd api

# Start infrastructure
docker-compose up -d postgres redis minio

# Install Python deps
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Download embedding model (one-time, ~80MB)
python scripts/download_model.py

# Start dev server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=app
```

### 10.2 Testing Strategy
| Test Type | Tool | Coverage Target |
|-----------|------|-----------------|
| Unit tests | pytest | 80% |
| Integration tests | pytest + TestClient | API endpoints |
| Load tests | locust | 100 QPS sustained |
| E2E tests | Playwright | Critical user flows |
| Security tests | OWASP ZAP | Quarterly scan |

---

## 11. Deployment Pipeline

```
Git Push to main
     │
     ▼
┌─────────────┐
│ GitHub Actions │
│   - Lint     │
│   - Test     │
│   - Build    │
│   - Scan     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Staging Env │ ← Auto-deploy, run smoke tests
│   (Docker)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Manual Gate │ ← Product team approval
│             │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Production  │ ← Blue-green deployment
│   (Docker)  │
└─────────────┘
```

---

## 12. Open Technical Questions

1. **GPU vs CPU for embeddings:** Do we need GPU for <100ms embedding latency at scale, or is CPU sufficient with batching?
2. **ChromaDB vs Qdrant:** At what merchant count does ChromaDB hit limits? Benchmark at 10K, 100K, 1M vectors.
3. **Real-time sync:** Should we use Shopify GraphQL subscriptions or polling for stores without webhook support?
4. **Multi-tenancy:** Separate ChromaDB collections per store vs single collection with store_id filter?
5. **Edge deployment:** Should we deploy search nodes close to merchants (CloudFlare Workers) for <50ms latency?

---

*End of TRD*
