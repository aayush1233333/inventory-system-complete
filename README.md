# 📦 StockFlow — Inventory & Order Management System

A full-stack inventory and order management system built with **FastAPI + React + PostgreSQL**, containerized with **Docker Compose**.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              Docker Compose Network               │
│                                                   │
│  ┌───────────┐   ┌────────────┐   ┌───────────┐  │
│  │  Frontend  │──▶│  Backend   │──▶│ PostgreSQL│  │
│  │  React +  │   │  FastAPI   │   │  Port     │  │
│  │  Nginx    │   │  Port 8000 │   │  5432     │  │
│  │  Port 80  │   │            │   │           │  │
│  └───────────┘   └────────────┘   └───────────┘  │
└──────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
inventory-system/
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment variable template
├── .gitignore
│
├── backend/                    # Python FastAPI service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py             # Entry point + CORS + routing
│       ├── core/
│       │   ├── config.py       # Pydantic Settings (env vars)
│       │   └── database.py     # SQLAlchemy engine + session
│       ├── models/
│       │   └── models.py       # SQLAlchemy ORM models
│       ├── schemas/
│       │   └── schemas.py      # Pydantic request/response schemas
│       └── routers/
│           ├── products.py     # CRUD + SKU uniqueness
│           ├── customers.py    # CRUD + email uniqueness
│           ├── orders.py       # Create w/ stock validation
│           └── dashboard.py    # Aggregate stats
│
└── frontend/                   # React SPA
    ├── Dockerfile              # Multi-stage build → Nginx
    ├── nginx.conf              # SPA routing + API proxy
    ├── package.json
    └── src/
        ├── App.js              # Routing + sidebar
        ├── index.css           # Full design system
        ├── lib/api.js          # Axios API client
        └── pages/
            ├── Dashboard.js    # Stats overview
            ├── Products.js     # Product CRUD table
            ├── Customers.js    # Customer CRUD table
            ├── Orders.js       # Order creation + status mgmt
            └── Inventory.js    # Low/out-of-stock alerts
```

---

## ⚙️ Business Rules Enforced

| Rule | Where |
|------|-------|
| Product SKU must be unique | `POST /api/v1/products` → 409 if duplicate |
| Customer email must be unique | `POST /api/v1/customers` → 409 if duplicate |
| Validate stock before order | `POST /api/v1/orders` → 422 if insufficient |
| Auto-deduct stock on order | `POST /api/v1/orders` (atomic with `FOR UPDATE`) |
| Restore stock on cancellation | `PATCH /api/v1/orders/{id}/status` |

---

## 🚀 Quick Start (Local with Docker)

### Prerequisites
- Docker Desktop (or Docker + Docker Compose)
- Git

### 1. Clone & configure

```bash
git clone https://github.com/YOUR_USERNAME/stockflow.git
cd stockflow

cp .env.example .env
# Edit .env — change passwords and SECRET_KEY
```

### 2. Launch all services

```bash
docker compose up --build
```

Wait ~60 seconds for first build. Services start in order: PostgreSQL → Backend → Frontend.

### 3. Open the app

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:80 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/api/docs |
| **API Docs (ReDoc)** | http://localhost:8000/api/redoc |

---

## 🔌 API Reference

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products (search, low_stock filter) |
| POST | `/api/v1/products` | Create product (unique SKU required) |
| GET | `/api/v1/products/{id}` | Get single product |
| PATCH | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/customers` | List customers (search filter) |
| POST | `/api/v1/customers` | Create customer (unique email) |
| GET | `/api/v1/customers/{id}` | Get single customer |
| PATCH | `/api/v1/customers/{id}` | Update customer |
| DELETE | `/api/v1/customers/{id}` | Delete customer |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders` | List orders (status/customer filter) |
| POST | `/api/v1/orders` | Create order + deduct stock |
| GET | `/api/v1/orders/{id}` | Get order with items |
| PATCH | `/api/v1/orders/{id}/status` | Update status (restores stock on cancel) |
| DELETE | `/api/v1/orders/{id}` | Delete order |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Aggregate stats for KPIs |

---

## ☁️ Free Deployment Guide

### Option A: Railway (Recommended — easiest)

Railway supports Docker and PostgreSQL natively with a free tier.

#### Backend + Database on Railway

1. Create account at [railway.app](https://railway.app)
2. New Project → **Deploy from GitHub repo**
3. Select your repository, set **Root Directory** to `backend`
4. Add a **PostgreSQL** plugin in the same project
5. Set environment variables in Railway dashboard:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=your-secure-secret
   APP_ENV=production
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```
6. Railway auto-detects the `Dockerfile` and deploys
7. Note your backend URL: `https://stockflow-backend.up.railway.app`

#### Frontend on Vercel

1. Create account at [vercel.com](https://vercel.com)
2. New Project → Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Set environment variables:
   ```
   REACT_APP_API_URL=https://stockflow-backend.up.railway.app
   ```
5. Vercel auto-detects React and builds with `npm run build`
6. Your app is live at: `https://stockflow.vercel.app`

---

### Option B: Render

#### Backend on Render

1. [render.com](https://render.com) → New → **Web Service**
2. Connect GitHub, select repo, set **Root Directory**: `backend`
3. **Environment**: Docker
4. Add environment variables (same as Railway)
5. Create a **PostgreSQL** database on Render and copy its URL

#### Frontend on Render (Static Site)

1. New → **Static Site** → Connect same repo
2. **Root Directory**: `frontend`
3. **Build Command**: `npm install && npm run build`
4. **Publish Directory**: `build`
5. Add env var: `REACT_APP_API_URL=https://your-backend.onrender.com`

---

### Option C: Fly.io + Supabase

1. Use [Supabase](https://supabase.com) free tier for PostgreSQL
2. Set `DATABASE_URL` to your Supabase connection string
3. Deploy backend to [Fly.io](https://fly.io) with `fly deploy`
4. Deploy frontend to Vercel or Netlify

---

## 🛠️ Development (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit with local DB creds
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `inventory_db` |
| `POSTGRES_USER` | DB user | `postgres` |
| `POSTGRES_PASSWORD` | DB password | ⚠️ Change this |
| `DATABASE_URL` | Full Postgres URL | Constructed from above |
| `SECRET_KEY` | App secret | ⚠️ Change this |
| `APP_ENV` | Environment | `development` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:80` |
| `REACT_APP_API_URL` | Backend URL for frontend | `""` (uses nginx proxy) |

---

## 📦 Docker Commands

```bash
# Start all services (rebuild images)
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Stop and remove volumes (⚠️ deletes DB data)
docker compose down -v

# Rebuild single service
docker compose up --build backend

# Open psql shell
docker compose exec db psql -U postgres -d inventory_db
```

---

## 🧪 Sample API Calls

```bash
# Create a product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","sku":"LAP-001","price":45000,"stock_quantity":20,"category":"Electronics"}'

# Create a customer
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"Priya Sharma","email":"priya@example.com","phone":"+91 98765 43210"}'

# Create an order (will fail if stock < quantity)
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"items":[{"product_id":1,"quantity":2}]}'
```

---

## 🗂️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router, Axios, react-hot-toast |
| Backend | Python 3.11, FastAPI, Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | PostgreSQL 15 |
| Containerization | Docker, Docker Compose |
| Reverse Proxy | Nginx (frontend) |
| Deployment | Vercel / Railway / Render / Fly.io |
