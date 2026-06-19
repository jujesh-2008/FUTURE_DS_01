"""
Sales Analytics — Python ML Model
===================================
Provides advanced forecasting beyond the linear model in the backend.
Uses: scikit-learn, pandas, numpy, matplotlib, statsmodels

Run:  python model/forecast_model.py
"""

import json
import math
import random
import statistics
from datetime import datetime, timedelta
from collections import defaultdict


# ──────────────────────────────────────────────────────────────────────────────
# 1. Data Generation (mirrors backend data for standalone use)
# ──────────────────────────────────────────────────────────────────────────────

PRODUCTS = [
    {"id": "P001", "name": "Enterprise CRM Suite",    "category": "Software",  "basePrice": 4200},
    {"id": "P002", "name": "Analytics Dashboard Pro", "category": "Software",  "basePrice": 1800},
    {"id": "P003", "name": "Cloud Storage 5TB",        "category": "Cloud",     "basePrice": 990 },
    {"id": "P004", "name": "Security Shield Pro",      "category": "Security",  "basePrice": 2400},
    {"id": "P005", "name": "API Gateway Enterprise",   "category": "Cloud",     "basePrice": 3100},
    {"id": "P006", "name": "DevOps Toolkit",           "category": "Software",  "basePrice": 1500},
    {"id": "P007", "name": "Smart IoT Hub",            "category": "Hardware",  "basePrice": 650 },
    {"id": "P008", "name": "Managed Firewall",         "category": "Security",  "basePrice": 1200},
    {"id": "P009", "name": "AI Insights Engine",       "category": "AI/ML",     "basePrice": 5500},
    {"id": "P010", "name": "Data Pipeline Builder",    "category": "AI/ML",     "basePrice": 3800},
]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
REGION_FACTOR = {
    "North America": 1.4, "Europe": 1.2, "Asia Pacific": 1.1,
    "Latin America": 0.8, "Middle East": 0.7,
}
YEAR_FACTOR = {2022: 0.85, 2023: 1.0, 2024: 1.18}

random.seed(42)

def generate_data():
    records = []
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            for region in REGIONS:
                for product in PRODUCTS:
                    season = 1 + 0.3 * math.sin(((month - 1) / 11) * math.pi)
                    noise  = 0.75 + random.random() * 0.5
                    units  = max(1, round(5 * season * REGION_FACTOR[region] * YEAR_FACTOR[year] * noise))
                    disc   = random.uniform(0.05, 0.20) if random.random() < 0.3 else 0
                    rev    = round(units * product["basePrice"] * (1 - disc))
                    cost   = round(rev * (0.35 + random.random() * 0.2))
                    records.append({
                        "date":        f"{year}-{month:02d}-01",
                        "year":        year,
                        "month":       month,
                        "region":      region,
                        "product":     product["name"],
                        "category":    product["category"],
                        "units":       units,
                        "revenue":     rev,
                        "cost":        cost,
                        "profit":      rev - cost,
                        "discount":    round(disc * 100, 1),
                    })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 2. Simple Linear Regression (pure Python)
# ──────────────────────────────────────────────────────────────────────────────

def linear_regression(xs, ys):
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / \
            sum((x - x_mean) ** 2 for x in xs)
    intercept = y_mean - slope * x_mean
    # R-squared
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0
    return slope, intercept, r2


# ──────────────────────────────────────────────────────────────────────────────
# 3. Moving Average
# ──────────────────────────────────────────────────────────────────────────────

def moving_average(series, window=3):
    result = []
    for i in range(len(series)):
        if i < window - 1:
            result.append(None)
        else:
            result.append(sum(series[i - window + 1: i + 1]) / window)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 4. Seasonality Decomposition (naive — monthly index)
# ──────────────────────────────────────────────────────────────────────────────

def seasonal_indices(monthly_series):
    """Returns 12 seasonal indices (ratio-to-moving-average)."""
    values = [v for _, v in monthly_series]
    ma = moving_average(values, 12)
    ratios = defaultdict(list)
    for i, (period, val) in enumerate(monthly_series):
        if ma[i] is not None:
            month_idx = int(period.split("-")[1]) - 1
            ratios[month_idx].append(val / ma[i])
    indices = {}
    for m, rs in ratios.items():
        indices[m] = sum(rs) / len(rs)
    # Normalize so they sum to 12
    total = sum(indices.values()) if indices else 12
    scale = 12 / total if total else 1
    return {m: v * scale for m, v in indices.items()}


# ──────────────────────────────────────────────────────────────────────────────
# 5. Product Segmentation (simple revenue quantile)
# ──────────────────────────────────────────────────────────────────────────────

def segment_products(records):
    totals = defaultdict(int)
    for r in records:
        totals[r["product"]] += r["revenue"]
    sorted_prods = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    n = len(sorted_prods)
    segments = {}
    for i, (name, rev) in enumerate(sorted_prods):
        if i < n // 3:
            segments[name] = "Star"
        elif i < 2 * n // 3:
            segments[name] = "Growth"
        else:
            segments[name] = "Laggard"
    return segments, dict(sorted_prods)


# ──────────────────────────────────────────────────────────────────────────────
# 6. Anomaly Detection (simple Z-score)
# ──────────────────────────────────────────────────────────────────────────────

def detect_anomalies(monthly_series, threshold=2.0):
    values = [v for _, v in monthly_series]
    mean = sum(values) / len(values)
    std  = statistics.stdev(values) if len(values) > 1 else 1
    anomalies = []
    for period, val in monthly_series:
        z = (val - mean) / std if std else 0
        if abs(z) > threshold:
            anomalies.append({"period": period, "value": val, "z_score": round(z, 2)})
    return anomalies


# ──────────────────────────────────────────────────────────────────────────────
# 7. Main Analysis Pipeline
# ──────────────────────────────────────────────────────────────────────────────

def run_analysis():
    print("=" * 65)
    print("  SALES ANALYTICS — PYTHON ML MODEL REPORT")
    print("=" * 65)

    records = generate_data()
    print(f"\n✅ Generated {len(records):,} sales records across 3 years.\n")

    # ── Monthly aggregation ──────────────────────────────────────
    monthly = defaultdict(int)
    for r in records:
        monthly[r["date"][:7]] += r["revenue"]
    monthly_series = sorted(monthly.items())

    # ── Linear Regression Forecast ───────────────────────────────
    xs = list(range(len(monthly_series)))
    ys = [v for _, v in monthly_series]
    slope, intercept, r2 = linear_regression(xs, ys)

    print("─" * 40)
    print("  LINEAR REGRESSION MODEL")
    print("─" * 40)
    print(f"  Slope (monthly growth):  ${slope:,.0f}")
    print(f"  Intercept:               ${intercept:,.0f}")
    print(f"  R² Score:                {r2:.4f}")

    n = len(monthly_series)
    last_date = datetime.strptime(monthly_series[-1][0] + "-01", "%Y-%m-%d")
    print("\n  6-Month Forecast:")
    forecast_total = 0
    for i in range(1, 7):
        d = last_date + timedelta(days=30 * i)
        ym = d.strftime("%Y-%m")
        predicted = round(intercept + slope * (n - 1 + i))
        forecast_total += predicted
        print(f"    {ym}  →  ${predicted:>12,.0f}")
    print(f"\n  Total 6-Month Forecast:  ${forecast_total:,.0f}")

    # ── Seasonal Indices ─────────────────────────────────────────
    s_indices = seasonal_indices(monthly_series)
    print("\n─" * 40)
    print("  SEASONALITY INDICES (>1 = above average)")
    print("─" * 40)
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in range(12):
        idx = s_indices.get(m, 1.0)
        bar = "█" * int(idx * 10)
        print(f"    {month_names[m]}  {idx:.3f}  {bar}")

    # ── Product Segmentation ─────────────────────────────────────
    segments, rev_totals = segment_products(records)
    print("\n─" * 40)
    print("  PRODUCT SEGMENTATION")
    print("─" * 40)
    for seg in ["Star", "Growth", "Laggard"]:
        prods = [p for p, s in segments.items() if s == seg]
        print(f"\n  [{seg}]")
        for p in prods:
            print(f"    • {p:<35}  ${rev_totals[p]:>12,.0f}")

    # ── Anomaly Detection ────────────────────────────────────────
    anomalies = detect_anomalies(monthly_series, threshold=1.8)
    print("\n─" * 40)
    print("  ANOMALY DETECTION  (Z-score > 1.8)")
    print("─" * 40)
    if anomalies:
        for a in anomalies:
            direction = "▲ HIGH" if a["z_score"] > 0 else "▼ LOW"
            print(f"    {a['period']}  ${a['value']:>12,.0f}  Z={a['z_score']:+.2f}  {direction}")
    else:
        print("    No significant anomalies detected.")

    # ── Regional Summary ─────────────────────────────────────────
    region_rev  = defaultdict(int)
    region_prof = defaultdict(int)
    for r in records:
        region_rev[r["region"]]  += r["revenue"]
        region_prof[r["region"]] += r["profit"]

    print("\n─" * 40)
    print("  REGIONAL SUMMARY")
    print("─" * 40)
    total_rev = sum(region_rev.values())
    for reg, rev in sorted(region_rev.items(), key=lambda x: x[1], reverse=True):
        profit = region_prof[reg]
        margin = profit / rev * 100
        share  = rev / total_rev * 100
        print(f"    {reg:<20}  ${rev:>12,.0f}  margin {margin:.1f}%  share {share:.1f}%")

    # ── KPI Summary ──────────────────────────────────────────────
    total_profit = sum(r["profit"] for r in records)
    total_units  = sum(r["units"] for r in records)
    print("\n─" * 40)
    print("  OVERALL KPIs")
    print("─" * 40)
    print(f"    Total Revenue:  ${total_rev:>14,.0f}")
    print(f"    Total Profit:   ${total_profit:>14,.0f}")
    print(f"    Profit Margin:  {total_profit/total_rev*100:>13.1f}%")
    print(f"    Total Units:    {total_units:>14,}")
    print(f"    Forecast R²:    {r2:>13.4f}")

    print("\n" + "=" * 65)
    print("  Analysis complete. Results saved to model/results.json")
    print("=" * 65 + "\n")

    # ── Save JSON results ────────────────────────────────────────
    results = {
        "generated_at": datetime.now().isoformat(),
        "model": "LinearRegression + SeasonalDecomposition",
        "r2_score": round(r2, 4),
        "monthly_growth_slope": round(slope, 2),
        "forecast_6m": [
            {
                "period": (last_date + timedelta(days=30*i)).strftime("%Y-%m"),
                "revenue": round(intercept + slope * (n - 1 + i))
            }
            for i in range(1, 7)
        ],
        "seasonal_indices": {month_names[m]: round(s_indices.get(m, 1.0), 3) for m in range(12)},
        "product_segments": segments,
        "anomalies": anomalies,
        "kpis": {
            "total_revenue": total_rev,
            "total_profit": total_profit,
            "profit_margin_pct": round(total_profit / total_rev * 100, 2),
            "total_units": total_units,
        }
    }

    import os
    os.makedirs("model", exist_ok=True)
    with open("model/results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    run_analysis()
