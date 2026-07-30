# AI Sales Forecasting Dashboard

A production-ready fullstack web application that uses **Machine Learning** (Linear Regression) to predict future sales based on historical data. Built with a **Flask REST API** backend and a **React** (Vite) frontend, deployed on **Vercel** with **Supabase PostgreSQL**.

## Features

- 🔐 **JWT Authentication** — Secure token-based login/logout
- 📊 **Dashboard** — Real-time stats (Total Sales, Profit, Orders) with interactive doughnut chart
- 📦 **Sales Management** — Full CRUD: Add, Edit, Delete, Search sales records
- 🧠 **AI Prediction** — Enter a future month and get ML-powered sales forecast (inference-only)
- 📈 **Sales Graph Analysis** — Toggle between Line Chart, Bar Chart, and Actual vs Predicted views
- 📤 **CSV Upload** — Upload training datasets with validation and database storage
- 📥 **Export** — Download sales data as Excel (.xlsx) or PDF report
- 🌙 **Modern UI** — Dark glassmorphic design with smooth animations

## Tech Stack

| Layer       | Technology                                         |
|-------------|---------------------------------------------------|
| Frontend    | React 19, Vite, React Router, Chart.js            |
| Backend     | Python, Flask, Flask-CORS, JWT (PyJWT)             |
| Database    | Supabase PostgreSQL (psycopg2)                     |
| ML/AI       | scikit-learn (LinearRegression), pandas, joblib     |
| Styling     | Vanilla CSS (dark glassmorphic)                    |
| Exports     | openpyxl (Excel), reportlab (PDF)                  |
| Deployment  | Vercel (Frontend + Backend Serverless)              |

## Architecture

```
┌─────────────────────┐     HTTPS/JSON      ┌─────────────────────────┐
│   React + Vite      │ ──────────────────►  │   Flask REST API        │
│   (Vercel Static)   │ ◄──────────────────  │   (Vercel Serverless)   │
│                     │   JWT Bearer Auth    │                         │
└─────────────────────┘                      │   ┌───────────────────┐ │
                                             │   │ Pre-trained Model │ │
                                             │   │ sales_model.pkl   │ │
                                             │   └───────────────────┘ │
                                             └──────────┬──────────────┘
                                                        │
                                                        ▼
                                             ┌─────────────────────┐
                                             │ Supabase PostgreSQL │
                                             │   (Cloud Database)  │
                                             └─────────────────────┘
```

## Project Structure

```
ai-powered-sales-dashboard/
├── client/                          # React frontend (deploy to Vercel)
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json                  # SPA rewrite rules
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                  # Router + Auth gate
│       ├── index.css                # Dark glassmorphic design system
│       ├── api.js                   # Centralized API client (JWT auth)
│       ├── context/
│       │   └── AuthContext.jsx      # Auth state management
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── TopNav.jsx
│       │   ├── StatCard.jsx
│       │   ├── SalesModal.jsx
│       │   └── Toast.jsx
│       └── pages/
│           ├── LoginPage.jsx
│           ├── DashboardPage.jsx
│           ├── SalesPage.jsx
│           ├── PredictionPage.jsx
│           └── AnalyticsPage.jsx
│
├── web_app/                         # Flask REST API (deploy to Vercel Serverless)
│   ├── app.py                       # Entry point — exports `app` for @vercel/python
│   ├── vercel.json                  # Vercel serverless config
│   ├── requirements.txt             # Python dependencies
│   ├── train_model.py               # Offline training script (developer only)
│   ├── routes/
│   │   ├── auth.py                  # Login, logout, auth status
│   │   ├── sales.py                 # Sales CRUD + stats
│   │   ├── prediction.py            # ML forecast + dataset + model info
│   │   ├── upload.py                # CSV upload + validation
│   │   └── exports.py               # Excel + PDF report generation
│   ├── services/
│   │   ├── database.py              # Supabase PostgreSQL connector + CRUD
│   │   ├── auth_service.py          # JWT token generation + verification
│   │   ├── model_loader.py          # Thread-safe cached model loader
│   │   └── forecast.py              # Prediction handler
│   ├── models/
│   │   └── sales_model.pkl          # Pre-trained ML model (committed to repo)
│   └── dataset/
│       └── current_dataset.csv      # Sample training dataset
│
├── README.md
└── .gitignore
```

## Environment Variables

### Backend (web_app)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ Yes | Supabase PostgreSQL connection string |
| `JWT_SECRET` | ✅ Yes | Secret key for signing JWT tokens |
| `SECRET_KEY` | Optional | Flask secret key (fallback for JWT_SECRET) |
| `ALLOWED_ORIGINS` | Optional | Comma-separated list of allowed CORS origins |

### Frontend (client)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | ✅ Yes (production) | Full URL of the deployed backend API (e.g., `https://your-backend.vercel.app/api`) |

## Local Development

### Prerequisites

- **Python 3.9+** installed
- **Node.js 18+** and **npm** installed
- A **Supabase** project (free tier works)

### 1. Set Up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings → Database** and copy the **Connection string** (URI format)
3. Use the **pooled connection** (port 6543) for serverless compatibility

### 2. Start the Backend

```bash
cd web_app

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Windows PowerShell:
$env:DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:6543/postgres"
$env:JWT_SECRET="your-secret-key-here"

# Linux/macOS:
# export DATABASE_URL="postgresql://..."
# export JWT_SECRET="your-secret-key-here"

# Start Flask server
python app.py
```

The API will start on **http://localhost:5000**.

### 3. Start the Frontend

```bash
cd client

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend will start on **http://localhost:5173** with API proxy to port 5000.

### 4. Login

- **Username:** `admin`
- **Password:** `admin123`

## Offline Model Training

The ML model is **pre-trained** and committed as `web_app/models/sales_model.pkl`. The deployed application does NOT retrain the model.

To retrain with new data:

```bash
cd web_app

# Train with default dataset
python train_model.py

# Train with custom CSV
python train_model.py --csv path/to/your_data.csv

# If DATABASE_URL is set, model metadata is also saved to Supabase
```

### CSV Format

```csv
Month,Sales
1,15000
2,17000
3,19000
...
```

## Deployment on Vercel

### Deploy the Backend

1. Go to [vercel.com](https://vercel.com) and import your repository
2. Set **Root Directory** to `web_app`
3. Add environment variables:
   - `DATABASE_URL` — Your Supabase connection string (pooled, port 6543)
   - `JWT_SECRET` — A strong random secret
   - `ALLOWED_ORIGINS` — Your frontend Vercel URL (e.g., `https://your-frontend.vercel.app`)
4. Click **Deploy**

### Deploy the Frontend

1. Import the same repository again (or use a separate Vercel project)
2. Set **Root Directory** to `client`
3. Set **Framework Preset** to `Vite`
4. Add environment variable:
   - `VITE_API_BASE_URL` — Your backend Vercel URL + `/api` (e.g., `https://your-backend.vercel.app/api`)
5. Click **Deploy**

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/login` | ❌ | Login with username/password, returns JWT |
| `POST` | `/api/logout` | ❌ | Logout (client-side token removal) |
| `GET` | `/api/auth/status` | ✅ | Verify JWT token validity |
| `GET` | `/api/sales` | ✅ | List all sales records |
| `POST` | `/api/sales` | ✅ | Create a new sale |
| `PUT` | `/api/sales/:id` | ✅ | Update a sale by ID |
| `DELETE` | `/api/sales/:id` | ✅ | Delete a sale by ID |
| `GET` | `/api/sales/search?product=` | ✅ | Search sales by product name |
| `GET` | `/api/stats` | ✅ | Dashboard statistics (totals) |
| `POST` | `/api/predict` | ✅ | ML sales prediction for a month |
| `GET` | `/api/model/info` | ✅ | Model metadata (accuracy, algorithm) |
| `GET` | `/api/dataset` | ✅ | Get uploaded dataset rows |
| `POST` | `/api/upload` | ✅ | Upload CSV dataset |
| `GET` | `/api/export/excel` | ✅ | Download Excel report |
| `GET` | `/api/export/pdf` | ✅ | Download PDF report |

### Authentication

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

The token is obtained from the `/api/login` response and expires after 24 hours.

## SQL Schema (Supabase)

Tables are auto-created on first startup. To manually create them:

```sql
-- Users
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Sales Records
CREATE TABLE IF NOT EXISTS sales(
    id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    total DOUBLE PRECISION NOT NULL,
    profit DOUBLE PRECISION NOT NULL
);

-- Dataset Rows (from CSV uploads)
CREATE TABLE IF NOT EXISTS dataset_rows(
    id SERIAL PRIMARY KEY,
    month INTEGER NOT NULL,
    sales DOUBLE PRECISION NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upload Metadata
CREATE TABLE IF NOT EXISTS uploaded_datasets(
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_count INTEGER NOT NULL
);

-- Prediction History
CREATE TABLE IF NOT EXISTS prediction_history(
    id SERIAL PRIMARY KEY,
    month INTEGER NOT NULL,
    predicted_sales DOUBLE PRECISION NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Metadata
CREATE TABLE IF NOT EXISTS model_metadata(
    id SERIAL PRIMARY KEY,
    accuracy DOUBLE PRECISION NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dataset_size INTEGER NOT NULL
);
```

## Changes from v1

| Area | Before | After |
|------|--------|-------|
| Database | SQLite + PostgreSQL dual-dialect | Supabase PostgreSQL only |
| Authentication | Flask session cookies | JWT Bearer tokens (PyJWT) |
| ML Training | Runtime background training | Inference-only (pre-trained .pkl) |
| Deployment | Render/PythonAnywhere + Gunicorn | Vercel Serverless (@vercel/python) |
| CSV Upload | Save to disk + auto-retrain | Validate + store in database |
| Dataset API | Read from filesystem CSV | Read from database table |
| Exports | Direct URL links (cookie auth) | Authenticated fetch + blob download |
| Passwords | Plaintext storage | Werkzeug hashed passwords |
| File Exports | Project-local tmp/ directory | System tempfile (Vercel /tmp) |
