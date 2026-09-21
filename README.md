# Velt — AI-Powered Storefront Semantic Search Engine

Velt is an MVP AI SaaS product under production hardening that replaces traditional keyword-matching search bars in eCommerce storefronts with semantic, vector-based search.

By mapping shopper intent to catalog product descriptions rather than exact spelling tags, Velt helps merchants improve product discovery, understand search traffic, and identify zero-result queries.

---

## 🚀 System Architecture

Velt is composed of three primary decoupled modules:

```mermaid
graph TD
    A[Shopper Storefront Widget] -->|Semantic Queries| B[FastAPI Backend Engine]
    C[Merchant Console Dashboard] -->|Catalog Sync & Configs| B
    B -->|Persist Embeddings| D[ChromaDB Vector Store]
    B -->|Metadata & API Keys| E[Neon PostgreSQL Database]
    B -->|Embedding Computation| F[Hugging Face Serverless Inference API / local PyTorch]
```

1. **FastAPI Vector Engine (`smartsearch-api`)**: Houses semantic vector embedding generation, store tenant metadata logic, search query log tracking, and ChromaDB vector persistence.
2. **Merchant Dashboard Console (`dashboard`)**: An elegant dashboard for merchants to manage multiple stores, upload product catalog feeds, view AI search metrics, customize the floating search widget, and generate developer API credentials.
3. **Storefront Search Widget (`widget`)**: A lightweight, zero-dependency floating action button and search overlay widget that connects shopper storefronts to the search vector engine.

---

## ✨ Features

- **Semantic Vector Search**: Powered by `all-MiniLM-L6-v2` generating 384-dimensional dense vectors to capture user shopping intent.
- **Multi-Tenant Architecture**: Supports multiple store workspaces isolated into distinct ChromaDB collections and Neon DB relational profiles.
- **Live Widget Studio**: Interactive double-pane preview customizer that allows merchants to brand primary accents, viewport scales (Desktop/Mobile), placeholder texts, and toggles (Price tags, Autocomplete, filters).
- **Search Traffic Analytics**: Custom-rendered SVG line charts mapping query volume, click-through rates (CTR), top conversion rankings, and zero-result search insights.
- **Remote Inference Option**: Set `USE_HF_INFERENCE=true` to use the Hugging Face Serverless Inference API instead of loading embedding model weights in the API process.
- **SPA Routing Resilience**: Standardized client-side routing configs (`vercel.json`) to prevent 404 router errors on page refreshes.

---

## 📂 Repository Structure

```text
├── dashboard/               # Vite + React + Tailwind CSS Merchant Console
│   ├── src/                 # Component tree, hooks, routing pages
│   ├── vercel.json          # SPA routing config for Vercel builds
│   └── package.json         
├── smartsearch-api/         # FastAPI backend app
│   ├── app/                 # Routers, databases, models, cores
│   ├── alembic/             # Neon SQL migration scripts
│   └── requirements.txt     
├── widget/                  # Frontend Storefront integration script
│   ├── widget.js            # Standalone Vanilla JS Floating search overlay
│   └── demo.html            # Merchant sandboxed storefront simulator
└── README.md
```

---

## 🛠️ Local Development Setup

### 1. Backend API Service

Navigate to `smartsearch-api` and configure your environment:

```bash
cd smartsearch-api
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Development and test tooling
pip install -r requirements-dev.txt
```

Create a `.env` file in the `smartsearch-api` root:

```env
DATABASE_URL=postgresql://neondb_owner:YOUR_NEON_PASSWORD@YOUR_NEON_HOST/neondb?sslmode=require
SECRET_KEY=your_jwt_auth_encryption_secret_key
USE_HF_INFERENCE=false
HF_TOKEN=your_huggingface_access_token_if_needed
DASHBOARD_BASE_URL=http://localhost:5173
BETA_INVITE_CODE=
```

Initialize your PostgreSQL tables and seed dummy data:

```bash
# Run migrations
alembic upgrade head

# Seed store, admin account, and product catalog
python seed_db.py
```

Fire up the FastAPI server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

---

### 2. Merchant Dashboard Console

Navigate to `dashboard` and setup dependencies:

```bash
cd ../dashboard
npm install
```

Create a `.env` file in the `dashboard` folder:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

Start the Vite development web app:

```bash
npm run dev
```
Open `http://localhost:5173` in your browser. Use the seeded credentials to log in:
* **Email**: `admin@example.com`
* **Password**: `Password123!`

---

### 3. Storefront Integration Sandbox

To run the storefront search widget demo locally:
1. Open the file `widget/demo.html` in your browser.
2. Provide your dynamic Store ID as a URL parameter to verify live product indexing:
   `widget/demo.html?store_id=your-store-uuid-here`

---

## Private Beta Deployment

Velt is approved for controlled staging and invite-only private beta use. Follow [staging-deployment-next-steps.md](smartsearch-api/docs/staging-deployment-next-steps.md) and [staging-validation-plan.md](smartsearch-api/docs/staging-validation-plan.md) before onboarding merchant data.

Copy `smartsearch-api/.env.staging.example` to the deployment secret store and replace every placeholder. Production startup requires a random `BETA_INVITE_CODE` of at least 16 characters; distribute it only to approved beta merchants. Then run:

```bash
docker compose -f smartsearch-api/docker/docker-compose.prod.yml up -d
```

Set `VELT_ENV_FILE` to use a differently named environment file. The stack completes migrations before starting the API, worker, and scheduler. Deploy the dashboard with `VITE_API_URL` pointing to the HTTPS API `/api/v1` endpoint and set `VITE_WIDGET_URL` when the widget is hosted on a separate controlled domain.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more details.
