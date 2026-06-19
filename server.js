const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// ─── Synthetic Sales Dataset ───────────────────────────────────────────────
const generateSalesData = () => {
  const products = [
    { id: 'P001', name: 'Enterprise CRM Suite',    category: 'Software',    basePrice: 4200 },
    { id: 'P002', name: 'Analytics Dashboard Pro', category: 'Software',    basePrice: 1800 },
    { id: 'P003', name: 'Cloud Storage 5TB',        category: 'Cloud',       basePrice: 990  },
    { id: 'P004', name: 'Security Shield Pro',      category: 'Security',    basePrice: 2400 },
    { id: 'P005', name: 'API Gateway Enterprise',   category: 'Cloud',       basePrice: 3100 },
    { id: 'P006', name: 'DevOps Toolkit',           category: 'Software',    basePrice: 1500 },
    { id: 'P007', name: 'Smart IoT Hub',            category: 'Hardware',    basePrice: 650  },
    { id: 'P008', name: 'Managed Firewall',         category: 'Security',    basePrice: 1200 },
    { id: 'P009', name: 'AI Insights Engine',       category: 'AI/ML',       basePrice: 5500 },
    { id: 'P010', name: 'Data Pipeline Builder',    category: 'AI/ML',       basePrice: 3800 },
  ];

  const regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East'];
  const months   = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const years    = [2022, 2023, 2024];

  const records = [];
  let id = 1;

  years.forEach(year => {
    months.forEach((month, mi) => {
      regions.forEach(region => {
        products.forEach(product => {
          const seasonFactor = 1 + 0.3 * Math.sin((mi / 11) * Math.PI);
          const regionFactor = { 'North America': 1.4, 'Europe': 1.2, 'Asia Pacific': 1.1, 'Latin America': 0.8, 'Middle East': 0.7 }[region];
          const yearFactor   = { 2022: 0.85, 2023: 1.0, 2024: 1.18 }[year];
          const noise        = 0.75 + Math.random() * 0.5;

          const units    = Math.max(1, Math.round(5 * seasonFactor * regionFactor * yearFactor * noise));
          const discount = Math.random() < 0.3 ? (0.05 + Math.random() * 0.15) : 0;
          const revenue  = Math.round(units * product.basePrice * (1 - discount));
          const cost     = Math.round(revenue * (0.35 + Math.random() * 0.2));

          records.push({
            id: id++,
            date: `${year}-${String(mi + 1).padStart(2, '0')}-01`,
            year, month, region,
            productId: product.id,
            productName: product.name,
            category: product.category,
            units,
            revenue,
            cost,
            profit: revenue - cost,
            discount: Math.round(discount * 100),
          });
        });
      });
    });
  });
  return records;
};

const SALES_DATA = generateSalesData();

// ─── Helper ────────────────────────────────────────────────────────────────
const filterData = (data, { year, region, category }) => {
  return data.filter(r =>
    (!year     || r.year     === +year)     &&
    (!region   || r.region   === region)    &&
    (!category || r.category === category)
  );
};

// ─── Routes ───────────────────────────────────────────────────────────────

// KPI Summary
app.get('/api/kpis', (req, res) => {
  const data = filterData(SALES_DATA, req.query);

  const totalRevenue = data.reduce((s, r) => s + r.revenue, 0);
  const totalProfit  = data.reduce((s, r) => s + r.profit,  0);
  const totalUnits   = data.reduce((s, r) => s + r.units,   0);
  const avgDiscount  = data.length ? (data.reduce((s, r) => s + r.discount, 0) / data.length).toFixed(1) : 0;
  const profitMargin = totalRevenue ? ((totalProfit / totalRevenue) * 100).toFixed(1) : 0;

  // YoY growth (compare last 2 years)
  const years = [...new Set(SALES_DATA.map(r => r.year))].sort();
  const curYear  = years[years.length - 1];
  const prevYear = years[years.length - 2];
  const curRev   = SALES_DATA.filter(r => r.year === curYear).reduce((s, r) => s + r.revenue, 0);
  const prevRev  = SALES_DATA.filter(r => r.year === prevYear).reduce((s, r) => s + r.revenue, 0);
  const yoyGrowth = prevRev ? (((curRev - prevRev) / prevRev) * 100).toFixed(1) : 0;

  res.json({ totalRevenue, totalProfit, totalUnits, avgDiscount, profitMargin, yoyGrowth });
});

// Monthly Revenue Trend
app.get('/api/trends/monthly', (req, res) => {
  const data = filterData(SALES_DATA, req.query);
  const map  = {};

  data.forEach(r => {
    const key = `${r.year}-${String(SALES_DATA.indexOf(r) % 12 + 1).padStart(2,'0')}`;
    // Use year-month from actual date
    const ym = r.date.slice(0, 7);
    if (!map[ym]) map[ym] = { period: ym, revenue: 0, profit: 0, units: 0 };
    map[ym].revenue += r.revenue;
    map[ym].profit  += r.profit;
    map[ym].units   += r.units;
  });

  const sorted = Object.values(map).sort((a, b) => a.period.localeCompare(b.period));
  res.json(sorted);
});

// Top Products
app.get('/api/products/top', (req, res) => {
  const data  = filterData(SALES_DATA, req.query);
  const limit = parseInt(req.query.limit) || 10;
  const map   = {};

  data.forEach(r => {
    if (!map[r.productId]) map[r.productId] = { productId: r.productId, name: r.productName, category: r.category, revenue: 0, units: 0, profit: 0 };
    map[r.productId].revenue += r.revenue;
    map[r.productId].units   += r.units;
    map[r.productId].profit  += r.profit;
  });

  const top = Object.values(map)
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, limit)
    .map(p => ({ ...p, margin: ((p.profit / p.revenue) * 100).toFixed(1) }));

  res.json(top);
});

// Category Breakdown
app.get('/api/categories', (req, res) => {
  const data = filterData(SALES_DATA, req.query);
  const map  = {};

  data.forEach(r => {
    if (!map[r.category]) map[r.category] = { category: r.category, revenue: 0, profit: 0, units: 0 };
    map[r.category].revenue += r.revenue;
    map[r.category].profit  += r.profit;
    map[r.category].units   += r.units;
  });

  const total = Object.values(map).reduce((s, c) => s + c.revenue, 0);
  const cats  = Object.values(map)
    .map(c => ({ ...c, share: ((c.revenue / total) * 100).toFixed(1), margin: ((c.profit / c.revenue) * 100).toFixed(1) }))
    .sort((a, b) => b.revenue - a.revenue);

  res.json(cats);
});

// Regional Performance
app.get('/api/regions', (req, res) => {
  const data = filterData(SALES_DATA, req.query);
  const map  = {};

  data.forEach(r => {
    if (!map[r.region]) map[r.region] = { region: r.region, revenue: 0, profit: 0, units: 0, deals: 0 };
    map[r.region].revenue += r.revenue;
    map[r.region].profit  += r.profit;
    map[r.region].units   += r.units;
    map[r.region].deals   += 1;
  });

  const total = Object.values(map).reduce((s, r) => s + r.revenue, 0);
  const regions = Object.values(map)
    .map(r => ({ ...r, share: ((r.revenue / total) * 100).toFixed(1), avgDeal: Math.round(r.revenue / r.deals), margin: ((r.profit / r.revenue) * 100).toFixed(1) }))
    .sort((a, b) => b.revenue - a.revenue);

  res.json(regions);
});

// Yearly Comparison
app.get('/api/trends/yearly', (req, res) => {
  const map = {};
  SALES_DATA.forEach(r => {
    if (!map[r.year]) map[r.year] = { year: r.year, revenue: 0, profit: 0, units: 0 };
    map[r.year].revenue += r.revenue;
    map[r.year].profit  += r.profit;
    map[r.year].units   += r.units;
  });
  const years = Object.values(map).sort((a, b) => a.year - b.year);
  res.json(years);
});

// Forecast (simple linear regression on monthly data)
app.get('/api/forecast', (req, res) => {
  const monthly = {};
  SALES_DATA.forEach(r => {
    const ym = r.date.slice(0, 7);
    if (!monthly[ym]) monthly[ym] = 0;
    monthly[ym] += r.revenue;
  });

  const series = Object.entries(monthly).sort((a, b) => a[0].localeCompare(b[0]));
  const n = series.length;
  const xs = series.map((_, i) => i);
  const ys = series.map(([, v]) => v);

  const xMean = xs.reduce((a, b) => a + b, 0) / n;
  const yMean = ys.reduce((a, b) => a + b, 0) / n;
  const slope = xs.reduce((acc, x, i) => acc + (x - xMean) * (ys[i] - yMean), 0)
               / xs.reduce((acc, x) => acc + (x - xMean) ** 2, 0);
  const intercept = yMean - slope * xMean;

  const lastDate = new Date(series[n - 1][0] + '-01');
  const forecast = [];
  for (let i = 1; i <= 6; i++) {
    const d = new Date(lastDate);
    d.setMonth(d.getMonth() + i);
    const ym = d.toISOString().slice(0, 7);
    const predicted = Math.round(intercept + slope * (n - 1 + i));
    forecast.push({ period: ym, revenue: predicted, type: 'forecast' });
  }

  const historical = series.slice(-12).map(([period, revenue]) => ({ period, revenue, type: 'actual' }));
  res.json([...historical, ...forecast]);
});

// Filters metadata
app.get('/api/filters', (req, res) => {
  res.json({
    years:      [...new Set(SALES_DATA.map(r => r.year))].sort(),
    regions:    [...new Set(SALES_DATA.map(r => r.region))].sort(),
    categories: [...new Set(SALES_DATA.map(r => r.category))].sort(),
  });
});

// Serve frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅  Sales Analytics running → http://localhost:${PORT}`));
