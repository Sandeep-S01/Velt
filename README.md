# Velt — AI-Powered Storefront Semantic Search Engine

Velt is a complete, production-ready AI SaaS product that replaces traditional keyword-matching search bars in eCommerce storefronts with a semantic, vector-based AI search. 

By mapping shopper search intents to catalog product descriptions rather than exact spelling tags, Velt helps merchants increase search conversions, understand user search traffic trends, and capture revenue from zero-result queries.

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
- **Low-Memory Runtime Optimization**: Features a dynamic switch (`USE_HF_INFERENCE=true`) to offload heavy neural network weights to the Hugging Face Serverless Inference API, keeping backend memory consumption well under 512MB for free cloud tiers (like Render).
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
```

Create a `.env` file in the `smartsearch-api` root:

```env
DATABASE_URL=postgresql://neondb_owner:YOUR_NEON_PASSWORD@YOUR_NEON_HOST/neondb?sslmode=require
SECRET_KEY=your_jwt_auth_encryption_secret_key
USE_HF_INFERENCE=false
HF_TOKEN=your_huggingface_access_token_if_needed
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

## ☁️ Production Deployment

### Backend Deploy (Render Web Service)
1. Link your GitHub repo to a new **Render Web Service** container.
2. Select **Python 3** environment and use:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. In **Environment Variables**, configure:
   - `USE_HF_INFERENCE=true`
   - `HF_TOKEN` = `your_free_huggingface_token`
   - Add your Neon DB connection string under `DATABASE_URL`.
   - Add your `SECRET_KEY`.
   - Add `PUBLIC_API_BASE_URL` pointing to your deployed API root (e.g. `https://velt-api.onrender.com`).

### Frontend Deploy (Vercel)
1. Create a new project in **Vercel** pointing to your repository.
2. Select `dashboard` as the **Root Directory**.
3. Under **Environment Variables**, add `VITE_API_URL` pointing to your deployed Render API (e.g. `https://velt-api.onrender.com/api/v1`). If the widget is not served from the dashboard domain, also add `VITE_WIDGET_URL`.
4. Click **Deploy**. Vercel will build the frontend assets and automatically apply the rewrite paths from `vercel.json` to handle client route redirects.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more details.
