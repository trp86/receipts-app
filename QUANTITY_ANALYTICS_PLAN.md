# 📊 Quantity Analytics - Implementation Plan

## ✅ Phase 1: Show Quantity in Frontend (DONE)

**What was implemented:**
- Backend now includes: `quantity`, `unit`, `unit_price` in API response
- Frontend displays:
  - Quantity badge: `×5` (orange gradient)
  - Unit price: `€0.85 each` (when quantity > 1)
  - Visual distinction for bulk purchases

**Example Display:**
```
H-Milch 1.5% 1l ×5          €4.25
€0.85 each
[Dairy Products / Milk]
```

**Status:** Deployed ✅

---

## 🎯 Phase 2: Quantity Analytics Dashboard

### Analytics to Build:

#### 1. **Bulk Purchase Insights** 🛒
**Query:** Items bought in quantity > 1
```sql
SELECT 
    item_name,
    category,
    AVG(quantity) as avg_quantity,
    COUNT(*) as times_purchased,
    SUM(quantity * unit_price) as total_spent
FROM dim_items
WHERE quantity > 1
GROUP BY item_name, category
ORDER BY avg_quantity DESC
LIMIT 10
```

**Show:**
- "Top 10 items you buy in bulk"
- "Milk: Average 5 bottles per purchase"
- "Savings by buying in bulk: €X"

---

#### 2. **Average Quantity per Category** 📈
**Query:**
```sql
SELECT 
    category,
    AVG(quantity) as avg_qty,
    SUM(quantity) as total_units,
    COUNT(*) as purchase_count
FROM dim_items
GROUP BY category
ORDER BY avg_qty DESC
```

**Show:**
- Bar chart: Average quantity by category
- "Dairy Products: 2.8 items per purchase"
- "Most bulk category: Beverages (4.2 avg)"

---

#### 3. **Quantity Trends Over Time** 📅
**Query:**
```sql
SELECT 
    DATE_TRUNC('month', f.receipt_date) as month,
    i.category,
    AVG(i.quantity) as avg_quantity,
    SUM(i.quantity) as total_units
FROM dim_items i
JOIN fact_receipts f ON i.receipt_key = f.receipt_key
WHERE f.user_id = ?
GROUP BY month, category
ORDER BY month DESC
```

**Show:**
- Line chart: Quantity trends by month
- "You're buying more in bulk recently!"
- "Milk purchases: 3/month → 5/month"

---

#### 4. **Unit Price Comparison** 💰
**Query:**
```sql
SELECT 
    item_name,
    category,
    AVG(unit_price) as avg_unit_price,
    MIN(unit_price) as best_price,
    MAX(unit_price) as highest_price,
    COUNT(*) as times_purchased
FROM dim_items
WHERE unit_price > 0
GROUP BY item_name, category
HAVING COUNT(*) > 1
ORDER BY (MAX(unit_price) - MIN(unit_price)) DESC
```

**Show:**
- "Best deals this month"
- "Milk: Best price €0.79 (current: €0.85)"
- "Price variation: €0.15 (21%)"

---

#### 5. **Inventory Projection** 📦
**Query:**
```sql
SELECT 
    item_name,
    category,
    SUM(quantity) as total_bought,
    COUNT(DISTINCT DATE(f.receipt_date)) as days_span,
    SUM(quantity) / COUNT(DISTINCT DATE(f.receipt_date)) as daily_rate
FROM dim_items i
JOIN fact_receipts f ON i.receipt_key = f.receipt_key
WHERE f.user_id = ? AND f.receipt_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY item_name, category
HAVING SUM(quantity) > 5
ORDER BY daily_rate DESC
```

**Show:**
- "Your consumption rate"
- "Milk: 5 bottles = ~7 days supply"
- "Next purchase suggested: 3 days"

---

### Dashboard Layout:

```
📊 Quantity Analytics

┌─────────────────────────────────────────┐
│ Bulk Purchase Summary                   │
│ • Items bought in bulk: 15              │
│ • Total units purchased: 142            │
│ • Average quantity: 2.3                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Top Bulk Items                          │
│ 🥛 Milk            ×5    (12 times)    │
│ 🧈 Butter          ×3    (8 times)     │
│ 🍕 Pizza           ×2    (15 times)    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Average Quantity by Category [Chart]    │
│ Beverages     ████████ 4.2             │
│ Dairy         ██████ 3.1               │
│ Frozen        ████ 2.5                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Best Unit Prices                        │
│ Milk    €0.79 (save €0.15 vs avg)     │
│ Butter  €1.89 (save €0.30 vs avg)     │
└─────────────────────────────────────────┘
```

---

## 🛠️ Implementation Steps:

### Backend:
1. **Create `analytics_quantity_service.py`**
   - `get_bulk_purchase_summary(user_id)`
   - `get_top_bulk_items(user_id, limit=10)`
   - `get_avg_quantity_by_category(user_id)`
   - `get_unit_price_insights(user_id)`
   - `get_quantity_trends(user_id, months=6)`

2. **Add API endpoints to `main.py`**
   - `GET /api/analytics/quantity/summary`
   - `GET /api/analytics/quantity/bulk-items`
   - `GET /api/analytics/quantity/by-category`
   - `GET /api/analytics/quantity/unit-prices`

### Frontend:
3. **Create components:**
   - `QuantityAnalytics.jsx` (main page)
   - `BulkItemsList.jsx`
   - `QuantityByCategory.jsx` (chart)
   - `UnitPriceComparison.jsx`

4. **Add routing:**
   - `/analytics/quantity` route
   - Link from main analytics dashboard

5. **Charts:**
   - Use Recharts for visualizations
   - Bar chart for categories
   - Line chart for trends

---

## ⏱️ Time Estimate:

- Backend queries: 30 minutes
- API endpoints: 15 minutes
- Frontend components: 45 minutes
- Charts: 30 minutes
- **Total: ~2 hours**

---

## 📝 Notes:

- MotherDuck already has quantity data in `dim_items`
- ETL job syncs this automatically
- All quantity data available immediately
- No schema changes needed
- Just add queries and UI

---

**Ready to build Phase 2?** This will give you powerful insights into your bulk buying patterns! 📊
