# Implementation Plan
## SmartSearch API — Semantic Search for E-commerce

**Version:** 1.0  
**Date:** 2026-06-22  
**Status:** Draft  
**Author:** Engineering Team

---

## 1. Project Overview

### 1.1 Goal
Build and launch a production-ready semantic search SaaS for e-commerce merchants in **8 weeks** (MVP), with a clear path to scale.

### 1.2 Build Philosophy
- **Week 1-2:** Core engine (search works, local machine)
- **Week 3-4:** API + ingestion (merchants can connect stores)
- **Week 5-6:** Dashboard + widget (merchants can see results)
- **Week 7-8:** Polish, billing, launch (first paying customers)

### 1.3 Success Criteria for Each Phase
| Phase | Deliverable | Success Criteria |
|-------|-------------|------------------|
| **Phase 1** | Local semantic engine | Search 1,000 products by meaning in < 200ms |
| **Phase 2** | REST API + ingestion | Connect Shopify store, sync products, search via API |
| **Phase 3** | Dashboard + JS widget | Merchant sees analytics, widget on live store |
| **Phase 4** | Billing + launch | First 10 paying customers, <$50 CAC |

---

## 2. Phase 1: Core Semantic Engine (Weeks 1-2)

### Week 1: Foundation & Local Prototype

#### Day 1-2: Project Setup
| Task | Time | Details | Output |
|------|------|---------|--------|
| Initialize repo | 2h | Git, Python 3.11, virtual env, pre-commit hooks | `smartsearch-api/` repo |
| Docker Compose | 4h | PostgreSQL 16, Redis 7, ChromaDB, MinIO | `docker-compose.yml` |
| Project structure | 2h | `app/`, `tests/`, `scripts/`, `docs/` | Clean directory layout |
| Dependency management | 2h | `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` | Locked dependencies |

**Directory Structure:**
```
smartsearch-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── search.py    # Search endpoints
│   │   │   ├── ingest.py    # Ingestion endpoints
│   │   │   ├── stores.py    # Store management
│   │   │   └── health.py    # Health checks
│   ├── core/
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Embedding model wrapper
│   │   ├── search_engine.py  # Semantic search logic
│   │   ├── chunking.py      # Text chunking
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── store_service.py
│   │   ├── product_service.py
│   │   └── search_service.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── security.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/
│   ├── download_model.py
│   └── seed_data.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   └── api.md
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

#### Day 3-4: Embedding Model & Chunking
| Task | Time | Details | Output |
|------|------|---------|--------|
| Download model | 1h | `all-MiniLM-L6-v2` (80MB) | Model cached locally |
| Embedding wrapper | 4h | `EmbeddingModel` class, batch encode, CPU optimization | `app/core/embeddings.py` |
| Text chunking | 4h | Recursive chunking, overlap, metadata preservation | `app/core/chunking.py` |
| Unit tests | 3h | Test chunking, embedding dimensions, batch sizes | `tests/unit/` |

**Key Code:**
```python
# app/core/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        return self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)

    def encode_single(self, text: str) -> np.ndarray:
        return self.model.encode([text])[0]
```

#### Day 5-7: ChromaDB Integration & Local Search
| Task | Time | Details | Output |
|------|------|---------|--------|
| ChromaDB client | 4h | Persistent client, collection management | `app/core/vector_store.py` |
| Document indexing | 4h | Add products, chunk, embed, store | `app/services/indexing_service.py` |
| Search implementation | 4h | Query embedding, similarity search, filtering | `app/core/search_engine.py` |
| Local demo script | 4h | CLI tool to index CSV and search | `scripts/demo_search.py` |
| Performance test | 4h | Benchmark 1K, 10K, 100K products | Latency report |

**Deliverable:** Local CLI tool that can:
1. Load a CSV of products
2. Index them into ChromaDB
3. Search by meaning with sub-second results

### Week 2: API Foundation & Data Layer

#### Day 8-10: PostgreSQL & SQLAlchemy
| Task | Time | Details | Output |
|------|------|---------|--------|
| Database models | 6h | Users, Stores, Products, API Keys (from schema doc) | `app/models/database.py` |
| Alembic migrations | 3h | Initial migration, migration scripts | `alembic/` |
| CRUD operations | 6h | Store service, product service, user service | `app/services/` |
| Database tests | 3h | Test CRUD, relationships, constraints | `tests/integration/` |

#### Day 11-12: FastAPI Skeleton
| Task | Time | Details | Output |
|------|------|---------|--------|
| FastAPI app setup | 4h | App factory, middleware, exception handlers | `app/main.py` |
| Health endpoints | 2h | `/health`, `/ready`, `/metrics` | Health check API |
| Auth middleware | 6h | API key validation, JWT for dashboard | `app/utils/security.py` |
| Rate limiting | 4h | Redis-based token bucket | `app/core/rate_limiter.py` |

#### Day 13-14: Core API Endpoints
| Task | Time | Details | Output |
|------|------|---------|--------|
| Search endpoint | 6h | POST `/api/v1/search`, validation, response formatting | `app/api/v1/search.py` |
| Ingest endpoint | 6h | POST `/api/v1/ingest`, CSV/JSON parsing, background job | `app/api/v1/ingest.py` |
| Store endpoints | 4h | CRUD for stores, platform connection | `app/api/v1/stores.py` |
| API docs | 4h | Auto-generated OpenAPI, Postman collection | Swagger UI |

**Deliverable:** Working local API with:
- `POST /api/v1/search` — semantic search
- `POST /api/v1/ingest` — add products
- `GET /api/v1/stores/{id}` — store management
- API key authentication
- Rate limiting

---

## 3. Phase 2: Merchant Integration (Weeks 3-4)

### Week 3: Platform Integrations & Sync

#### Day 15-17: Shopify Integration
| Task | Time | Details | Output |
|------|------|---------|--------|
| Shopify OAuth | 6h | OAuth flow, token storage, scope management | `app/integrations/shopify.py` |
| Product sync | 8h | Fetch products, variants, images, transform to our schema | `app/services/shopify_sync.py` |
| Webhook handler | 6h | Receive product updates, queue for re-indexing | `app/api/v1/webhooks.py` |
| Sync scheduler | 4h | Celery beat schedule, daily sync jobs | `app/tasks/sync.py` |

**Shopify OAuth Flow:**
```
Merchant clicks "Connect Shopify" → Redirect to Shopify OAuth
→ Merchant approves → Callback with auth code
→ Exchange for access token → Store in encrypted field
→ Trigger initial product sync (background job)
→ Webhook subscriptions registered
→ Email: "Your store is connected!"
```

#### Day 18-19: Background Jobs & Celery
| Task | Time | Details | Output |
|------|------|---------|--------|
| Celery setup | 4h | Worker, beat, Redis broker, task definitions | `app/tasks/` |
| Ingestion worker | 6h | Process CSV, chunk, embed, index | `app/tasks/ingest.py` |
| Sync worker | 4h | Platform sync, delta updates, error handling | `app/tasks/sync.py` |
| Notification worker | 4h | Email alerts, completion notifications | `app/tasks/notifications.py` |

#### Day 20-21: CSV/JSON Upload & Manual Ingestion
| Task | Time | Details | Output |
|------|------|---------|--------|
| File upload API | 4h | Multipart upload, validation, MinIO storage | `app/api/v1/upload.py` |
| CSV parser | 6h | pandas, column mapping, error reporting | `app/utils/csv_parser.py` |
| JSON parser | 2h | Schema validation, nested flattening | `app/utils/json_parser.py` |
| Upload dashboard | 4h | Progress tracking, error display, retry | Upload UI |

### Week 4: Widget & Dashboard Backend

#### Day 22-24: JS Widget API
| Task | Time | Details | Output |
|------|------|---------|--------|
| Widget config API | 4h | GET config by store_id, CORS enabled | `app/api/v1/widget.py` |
| CORS handling | 2h | Whitelist domains, preflight, security | Middleware |
| Widget search endpoint | 4h | Simplified search, formatted for widget | `app/api/v1/widget_search.py` |
| Autocomplete API | 4h | Prefix matching, popular queries, caching | `app/api/v1/autocomplete.py` |

#### Day 25-26: Analytics Backend
| Task | Time | Details | Output |
|------|------|---------|--------|
| ClickHouse setup | 4h | Docker container, schema creation | `docker-compose.yml` update |
| Event tracking | 6h | Pixel endpoint, event ingestion, batching | `app/api/v1/events.py` |
| Aggregation jobs | 4h | Daily rollups, materialized views | `app/tasks/analytics.py` |
| Analytics API | 4h | Dashboard data endpoints, time-series | `app/api/v1/analytics.py` |

#### Day 27-28: Testing & Integration
| Task | Time | Details | Output |
|------|------|---------|--------|
| Integration tests | 8h | End-to-end: upload → index → search → analytics | `tests/e2e/` |
| Load testing | 4h | Locust, 100 concurrent users, latency validation | Load test report |
| Bug fixes | 8h | Fix critical issues from testing | Stable build |

**Deliverable:** Working system where:
1. Merchant connects Shopify store
2. Products auto-sync to vector index
3. Search API returns semantic results
4. Widget can be embedded on store
5. Analytics track searches and clicks

---

## 4. Phase 3: Frontend & Dashboard (Weeks 5-6)

### Week 5: Dashboard (React)

#### Day 29-31: Dashboard Setup & Auth
| Task | Time | Details | Output |
|------|------|---------|--------|
| React project setup | 4h | Vite, TypeScript, Tailwind, React Router | `dashboard/` |
| Auth context | 4h | Login, register, JWT storage, protected routes | `src/contexts/AuthContext.tsx` |
| API client | 4h | Axios wrapper, interceptors, error handling | `src/lib/api.ts` |
| Layout components | 4h | Sidebar, header, page layout, navigation | `src/components/Layout/` |

#### Day 32-34: Dashboard Pages
| Task | Time | Details | Output |
|------|------|---------|--------|
| Store list page | 4h | Table of stores, status, actions | `src/pages/Stores/` |
| Store detail page | 6h | Overview, metrics, sync status, settings | `src/pages/StoreDetail/` |
| Analytics page | 6h | Charts, top queries, no-results, conversion | `src/pages/Analytics/` |
| Settings page | 4h | Widget config, search settings, billing | `src/pages/Settings/` |

**Dashboard Pages:**
```
/                    → Login/Register (public)
/dashboard           → Overview (stores list, quick stats)
/dashboard/stores/:id → Store detail (metrics, sync, products)
/dashboard/stores/:id/analytics → Search analytics (charts, tables)
/dashboard/stores/:id/products → Product list (index status, actions)
/dashboard/stores/:id/settings → Widget config, search settings
/dashboard/billing   → Subscription, invoices, usage
/dashboard/docs      → API docs, integration guides
```

#### Day 35: Dashboard Polish
| Task | Time | Details | Output |
|------|------|---------|--------|
| Responsive design | 4h | Mobile layout, tablet adjustments | Responsive dashboard |
| Loading states | 3h | Skeletons, spinners, progress bars | Smooth UX |
| Error states | 3h | Empty states, error boundaries, retry | Resilient UI |

### Week 6: JS Widget & Landing Page

#### Day 36-38: JS Widget (Vanilla JS)
| Task | Time | Details | Output |
|------|------|---------|--------|
| Widget core | 6h | Search bar, results container, event handling | `widget/src/widget.ts` |
| Styling | 4h | CSS-in-JS, customizable variables, responsive | `widget/src/styles.css` |
| Autocomplete | 4h | Debounced input, suggestion dropdown, keyboard nav | `widget/src/autocomplete.ts` |
| Result rendering | 4h | Product cards, images, prices, match badges | `widget/src/results.ts` |
| Filters | 4h | Price range, category, availability | `widget/src/filters.ts` |

**Widget Architecture:**
```javascript
// widget/src/widget.ts
class SmartSearchWidget {
  constructor(config) {
    this.storeId = config.storeId;
    this.apiUrl = config.apiUrl || 'https://api.smartsearch.io';
    this.theme = config.theme || 'light';
    this.position = config.position || 'bottom-right';
    this.init();
  }

  init() {
    this.renderTrigger();    // Floating search button
    this.renderOverlay();    // Search overlay (hidden)
    this.bindEvents();       // Click, keydown, resize
  }

  async search(query) {
    const response = await fetch(`${this.apiUrl}/widget/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, store_id: this.storeId })
    });
    return response.json();
  }

  renderResults(results) {
    // Render product cards, filters, pagination
  }
}

// Usage: <script src="cdn.smartsearch.io/widget.js" data-store-id="xxx"></script>
```

#### Day 39-40: Landing Page & Marketing
| Task | Time | Details | Output |
|------|------|---------|--------|
| Landing page | 8h | Hero, features, pricing, demo, testimonials | `landing/` |
| Demo widget | 4h | Interactive demo on landing page | Live demo |
| Pricing page | 4h | Tier comparison, FAQ, CTA | Pricing page |
| Docs site | 4h | API docs, integration guides, SDK reference | `docs/` |

---

## 5. Phase 4: Billing, Launch & Polish (Weeks 7-8)

### Week 7: Billing & Payments

#### Day 41-43: Stripe Integration
| Task | Time | Details | Output |
|------|------|---------|--------|
| Stripe setup | 4h | Account, products, prices, webhooks | Stripe dashboard |
| Checkout flow | 6h | Stripe Checkout, customer portal, invoices | `app/services/billing.py` |
| Subscription logic | 6h | Tier enforcement, usage limits, upgrades/downgrades | `app/services/subscription.py` |
| Webhook handling | 4h | Payment success, failure, cancellation | `app/api/v1/stripe_webhooks.py` |

**Billing Flow:**
```
Merchant clicks "Upgrade" → Stripe Checkout
→ Payment success → Webhook updates subscription
→ Immediate feature unlock
→ Email: "Welcome to Pro!"
→ Usage limits updated in Redis
```

#### Day 44-45: Usage Tracking & Limits
| Task | Time | Details | Output |
|------|------|---------|--------|
| Usage counters | 4h | Increment on search, check before processing | Middleware |
| Limit enforcement | 4h | 429 response when limit exceeded, upgrade prompt | Error handling |
| Usage alerts | 4h | Email at 50%, 85%, 100% of limit | `app/tasks/usage_alerts.py` |
| Invoice generation | 4h | Monthly usage reports, overage billing | `app/tasks/invoicing.py` |

### Week 8: Launch Preparation

#### Day 46-48: Production Deployment
| Task | Time | Details | Output |
|------|------|---------|--------|
| VPS setup | 4h | Hetzner/DigitalOcean, Ubuntu, Docker, SSL | Production server |
| Docker deployment | 4h | Compose production, env vars, secrets | `docker-compose.prod.yml` |
| Nginx config | 4h | Reverse proxy, SSL, rate limiting, caching | `nginx.conf` |
| Monitoring | 4h | Prometheus, Grafana, Sentry, uptime checks | Monitoring stack |
| Backup setup | 4h | Automated DB backups, S3 sync | Backup scripts |

#### Day 49-50: Testing & QA
| Task | Time | Details | Output |
|------|------|---------|--------|
| Security audit | 4h | OWASP ZAP scan, dependency check | Security report |
| Performance test | 4h | Load test, latency validation, stress test | Performance report |
| User acceptance | 4h | Beta merchant testing, feedback collection | Feedback doc |
| Bug fixes | 8h | Critical fixes from testing | Stable release |

#### Day 51-52: Launch
| Task | Time | Details | Output |
|------|------|---------|--------|
| Soft launch | 4h | 10 beta merchants, monitor closely | Beta cohort |
| Feedback iteration | 4h | Fix top 5 issues from beta | Improved product |
| Public launch | 4h | Product Hunt, Reddit, Twitter, email list | Public announcement |
| Support setup | 4h | Help desk, FAQ, chat widget, documentation | Support system |

**Launch Checklist:**
- [ ] SSL certificates valid
- [ ] Stripe live mode active
- [ ] Email sending configured (SendGrid)
- [ ] Sentry error tracking live
- [ ] Monitoring dashboards ready
- [ ] Backup system tested
- [ ] Documentation complete
- [ ] Support channels open
- [ ] Pricing page accurate
- [ ] Privacy policy + ToS published

---

## 6. Post-Launch Roadmap (Months 3-6)

### Month 3: Growth & Optimization
| Feature | Effort | Impact |
|---------|--------|--------|
| WooCommerce integration | 1 week | +30% addressable market |
| Visual search (image upload) | 2 weeks | Differentiation |
| A/B testing framework | 1 week | Prove ROI to merchants |
| Affiliate/referral program | 3 days | Organic growth |

### Month 4: Scale & Enterprise
| Feature | Effort | Impact |
|---------|--------|--------|
| Multi-language search | 1 week | International expansion |
| White-label widget | 1 week | Agency market |
| Custom embedding models | 2 weeks | Enterprise differentiation |
| SLA & dedicated infrastructure | 1 week | Enterprise sales |

### Month 5-6: Platform & Ecosystem
| Feature | Effort | Impact |
|---------|--------|--------|
| Shopify App Store listing | 1 week | Distribution |
| WordPress/WooCommerce plugin | 1 week | Distribution |
| Partner API for agencies | 2 weeks | Channel sales |
| Marketplace (app ecosystem) | 4 weeks | Network effects |

---

## 7. Risk Mitigation & Contingency

### Risk 1: ChromaDB Doesn't Scale
| Trigger | Mitigation | Timeline |
|---------|------------|----------|
| >100ms search latency at 10K products | Migrate to Qdrant or Milvus | 1 week |
| >500ms at 50K products | Implement caching layer, shard by store | 3 days |
| Collection corruption | Daily backups, automatic restore | Immediate |

### Risk 2: Merchant Acquisition Too Slow
| Trigger | Mitigation | Timeline |
|---------|------------|----------|
| <50 signups in first month | Launch on Product Hunt, Hacker News | 3 days |
| <5% free-to-paid conversion | Add onboarding emails, live demo | 1 week |
| High churn (>10%) | Exit interviews, feature prioritization | 2 weeks |

### Risk 3: Technical Debt Accumulation
| Trigger | Mitigation | Timeline |
|---------|------------|----------|
| Test coverage <70% | Dedicated testing week | 1 week |
| API response time degrading | Performance profiling, optimization | 3 days |
| Database size growing fast | Archiving strategy, data retention | 1 week |

---

## 8. Team & Resource Requirements

### MVP Team (8 weeks)
| Role | Effort | Responsibility |
|------|--------|---------------|
| **Full-stack Developer** | 100% | Backend API, integrations, deployment |
| **Frontend Developer** | 75% | Dashboard, widget, landing page |
| **ML/AI Engineer** | 50% | Embedding models, search quality, tuning |
| **DevOps Engineer** | 25% | Infrastructure, CI/CD, monitoring (week 7-8) |
| **Designer** | 25% | UI/UX, branding, widget design (week 5-6) |
| **Product Manager** | 25% | Requirements, prioritization, launch (week 7-8) |

### Tools & Services Budget (Monthly)
| Service | Cost | Purpose |
|---------|------|---------|
| Hetzner/DigitalOcean VPS | $40 | Production server (4 vCPU, 8GB) |
| CloudFlare | $0 | CDN, DNS, SSL (free tier) |
| SendGrid | $0 | Email (100/day free) |
| Sentry | $0 | Error tracking (5K events free) |
| Stripe | $0 + 2.9% | Payments (no monthly fee) |
| Domain | $12/year | smartsearch.io |
| **Total Fixed** | **~$40/month** | |

---

## 9. Key Milestones & Decision Points

| Date | Milestone | Decision |
|------|-----------|----------|
| **Week 1 Friday** | Local search works | Continue to API layer? |
| **Week 2 Friday** | REST API functional | Ready for Shopify integration? |
| **Week 4 Friday** | Shopify sync + widget API | Ready for frontend? |
| **Week 6 Friday** | Dashboard + widget complete | Ready for billing? |
| **Week 8 Friday** | Production deployed | Ready for beta launch? |
| **Month 3** | 50 active merchants | Invest in growth or product? |
| **Month 6** | $5K MRR | Raise seed or bootstrap? |

---

## 10. Definition of Done (MVP)

### Functional Requirements
- [x] Merchant can connect Shopify store in < 5 minutes
- [x] Products auto-sync and are searchable by meaning
- [x] JS widget can be added to store with copy-paste
- [x] Dashboard shows search analytics and insights
- [x] Search latency < 200ms for 1,000 products
- [ ] Billing supports Free, Starter ($29), Pro ($79) tiers

### Non-Functional Requirements
- [ ] 99.9% uptime (measured over 30 days)
- [ ] API handles 100 concurrent searches
- [ ] Data encrypted at rest and in transit
- [ ] GDPR-compliant data deletion
- [x] Mobile-responsive dashboard and widget
- [x] Documentation covers all API endpoints

### Business Requirements
- [ ] 10 beta merchants actively using product
- [ ] 2+ paying customers by week 8
- [ ] <$50 customer acquisition cost
- [ ] Support response time < 24 hours
- [ ] Public launch with 50+ signups in first week

---

*End of Implementation Plan*
