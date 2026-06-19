# 📊 SalesIQ — Business Sales Performance Analytics

A full-stack business intelligence platform for analyzing sales data, identifying revenue trends, tracking KPIs, and generating AI-powered insights.

---

## 🚀 Project Overview

SalesIQ provides a **client-ready analytics dashboard** with:

| Feature | Details |
|---|---|
| **KPI Cards** | Revenue, Profit, Margin, Units, AOV, Discount |
| **Revenue Analysis** | Monthly / Quarterly trends, Category breakdown |
| **Regional Performance** | Bar charts, Radar chart, Scorecard table |
| **Product Rankings** | Top-10 leaderboard, margin analysis |
| **Customer Segments** | Enterprise / Mid-Market / SMB comparison |
| **ML Forecast** | 6-month revenue forecast (Linear Regression) |
| **AI Insights** | Automated recommendations from the data |
| **Heatmap** | Region × Category revenue matrix |
| **CSV Export** | Filtered data download |

---

## 🗂 Project Structure

```
sales-analytics/
├── backend/
│   ├── app.py                # Flask REST API (8 endpoints)
│   └── requirements.txt      # Python dependencies
├── frontend/
│   └── index.html            # Single-file React-free dashboard
├── ml_model/
│   └── analytics.py          # Pandas analytics + sklearn forecasting
├── data/
│   ├── generate_data.py      # Synthetic dataset generator (2000 rows)
│   ├── sales_data.csv        # Generated dataset
│   └── insights.json         # Pre-computed insights cache
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- A modern web browser (Chrome, Firefox, Edge)

### 1. Clone / Download the project
```bash
git clone <repo-url>
cd sales-analytics
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install Python dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Generate the dataset
```bash
python data/generate_data.py
```
This creates `data/sales_data.csv` with 2000 synthetic sales records spanning Jan 2023 – Jul 2024.

### 5. Run the backend API
```bash
python backend/app.py
```
API will be available at `http://localhost:5000`

### 6. Open the frontend
Open `frontend/index.html` directly in your browser **or** serve it:
```bash
# Simple HTTP server (Python)
cd frontend
python -m http.server 3000
# Then visit http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/filters` | Available filter values |
| `GET` | `/api/kpis` | Key performance indicators |
| `GET` | `/api/revenue/category` | Revenue breakdown by category |
| `GET` | `/api/revenue/region` | Revenue breakdown by region |
| `GET` | `/api/revenue/monthly` | Monthly revenue time series |
| `GET` | `/api/revenue/quarterly` | Quarterly aggregates |
| `GET` | `/api/products/top` | Top N products (default: 10) |
| `GET` | `/api/segments` | Customer segment analysis |
| `GET` | `/api/forecast` | 6-month revenue forecast (ML) |
| `GET` | `/api/heatmap` | Region × Category matrix |
| `GET` | `/api/insights/ai` | AI-generated recommendations |
| `GET` | `/api/export/csv` | Download filtered CSV |
| `POST`| `/api/upload` | Upload custom CSV dataset |

### Query Parameters (filters, apply to most endpoints)
```
?region=Europe&category=Hardware&segment=Enterprise&year=2023
```

### Example
```bash
curl "http://localhost:5000/api/kpis?region=Europe&year=2024"
curl "http://localhost:5000/api/products/top?n=5&category=Software"
curl "http://localhost:5000/api/forecast"
```

---

## 🤖 ML Model

Located in `ml_model/analytics.py`, the model includes:

### Revenue Forecasting
- **Algorithm**: Scikit-learn `LinearRegression`
- **Features**: Month index (time series)
- **Output**: 6-month ahead revenue forecast
- **Metrics**: R², MAE
- **Training**: Automatic on each API call (fast, ~10ms)

### Feature Importance
- **Algorithm**: `RandomForestRegressor`  
- **Features**: Region, Category, Units, Avg Discount
- **Output**: Driver importance weights for profit prediction

### To run standalone:
```bash
python ml_model/analytics.py
# Output: data/insights.json
```

---

## 📊 Dataset Schema

`data/sales_data.csv` — 2000 rows, 15 columns:

| Column | Type | Description |
|---|---|---|
| `date` | str | Transaction date (YYYY-MM-DD) |
| `month` | str | Year-Month (YYYY-MM) |
| `quarter` | str | Quarter label (Q1 2023) |
| `year` | int | Year |
| `region` | str | Geographic region (5 regions) |
| `category` | str | Product category (5 types) |
| `product` | str | Product name (25 SKUs) |
| `salesperson` | str | Rep ID (30 reps) |
| `units` | int | Units sold |
| `unit_price` | float | Price per unit ($) |
| `discount_pct` | float | Discount applied (%) |
| `revenue` | float | Gross revenue ($) |
| `cost` | float | Cost of goods ($) |
| `profit` | float | Net profit ($) |
| `customer_segment` | str | Enterprise / Mid-Market / SMB |

---

## 📱 Using Your Own Data

### Option A — Replace the CSV
Replace `data/sales_data.csv` with your own file. Ensure these columns exist:
- `revenue`, `profit`, `category`, `region`, `customer_segment`, `month`, `product`, `units`, `discount_pct`

### Option B — API Upload
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@your_sales_data.csv"
```

---

## 🏗 Production Deployment

### Backend (Gunicorn + Nginx)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Frontend
Deploy `frontend/index.html` to any static host:
- **Netlify**: drag & drop the file
- **GitHub Pages**: push to `gh-pages` branch
- **Vercel**: `vercel --prod`

Update the API base URL in `frontend/index.html`:
```javascript
const API_BASE = 'https://your-backend.com';
```

### Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r backend/requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

---

## 📈 Key Business Insights (from sample data)

| Insight | Finding |
|---|---|
| **Top Category** | Hardware ($16.6M, 47.9% of revenue) |
| **Top Region** | Middle East & Africa ($7.6M) |
| **Best Margin** | Services (45.6%) |
| **Top Product** | Network Switch ($3.8M) |
| **Growth Opportunity** | Services revenue growing fastest |
| **Risk** | Average 12.6% discount rate needs review |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript (ES6+) |
| **Charts** | Chart.js 4.4 |
| **Backend** | Python 3 + Flask |
| **Analytics** | Pandas, NumPy |
| **ML Model** | Scikit-learn (LinearRegression, RandomForestRegressor) |
| **Data** | CSV (easily swappable with PostgreSQL/MySQL) |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

*Built as a Business Sales Performance Analytics solution demonstrating end-to-end data engineering, ML forecasting, and interactive data visualization.*
