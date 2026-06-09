# Changelog

All notable changes to this project will be documented in this file.

---

## [v1.1.0] - 2026-06-10

### 🎉 Major Features

#### Quantity Analytics Dashboard
- **5 Analytics Views**: Comprehensive bulk buying insights
  - Bulk purchase summary (items in bulk, total units, avg quantity)
  - Top bulk items list with purchase frequency
  - Average quantity by category (bar chart)
  - Unit price insights with savings calculations
  - Quantity trends over time (line chart)
- **Tab Navigation**: Added Spending | Quantity tabs in Analytics
- **Real-time Insights**: Track bulk buying patterns across all receipts

### 🔧 Backend

#### New Services
- `analytics_quantity_service.py` - 5 analytics functions
  - `get_bulk_purchase_summary()`
  - `get_top_bulk_items()`
  - `get_avg_quantity_by_category()`
  - `get_unit_price_insights()`
  - `get_quantity_trends()`

#### New API Endpoints
- `GET /api/analytics/quantity/summary`
- `GET /api/analytics/quantity/bulk-items`
- `GET /api/analytics/quantity/by-category`
- `GET /api/analytics/quantity/unit-prices`
- `GET /api/analytics/quantity/trends`

#### Tests
- Added `test_quantity_analytics.py` - Full test suite

### 🎨 Frontend

#### New Components
- `QuantityAnalytics.jsx` - Main dashboard component
- `QuantityAnalytics.css` - Responsive styling
- Tab navigation in Analytics component

#### Features
- Summary cards (3 metrics)
- Bulk items list with colorful cards
- Category bar chart (Recharts)
- Unit price comparison table
- Trends line chart with multiple categories
- Euro currency symbols (€) throughout

#### API Integration
- 5 new API client functions in `api.js`

### 🐛 Bug Fixes

- **Currency Display**: Fixed all $ to € symbols
- **Template Literals**: Fixed currency formatting in template strings
- **Type Conversion**: Fixed Decimal to float conversion in price calculations
- **Netlify Deploy**: Fixed publish path from `frontend/frontend/dist` to `frontend/dist`

### 🧹 Cleanup

#### Removed Files (10 tracked + 6 untracked)
- Old documentation: `DEPLOYMENT_OLD.md`, `ETL_TEST.md`, `ETL_TEST_RESULTS.md`, `plan.md`
- Old tests: `test_db.py`, `test_webhook.py`, `test_upload_curl.sh`
- Backend tests: `test_database.py`, `test_upload.py`
- Temporary docs: 6 untracked markdown files

#### Updated
- `.gitignore`: Added `*.duckdb` files

#### Lines Changed
- **Added**: 1,604 lines (new features)
- **Removed**: 946 lines (cleanup)

### 📊 Statistics

**Development Time**: ~2.5 hours  
**Files Modified**: 10 files  
**Commits**: 13 commits  
**API Endpoints**: 5 new endpoints  
**Test Coverage**: 5/5 endpoints tested  

### 🚀 Deployment

- **Backend**: Deployed to Render ✅
- **Frontend**: Deployed to Netlify ✅
- **Status**: Fully functional in production
- **URLs**:
  - Frontend: https://app-receiptscan.netlify.app
  - Backend: https://receipts-app-v1co.onrender.com

### 📝 Documentation

- `QUANTITY_ANALYTICS_BACKEND.md` - Backend implementation guide
- `QUANTITY_ANALYTICS_PLAN.md` - Phase 2 planning document
- `CHANGELOG.md` - This file

---

## [v1.0.0] - 2026-06-05

### Initial Release

#### Features
- Receipt scanning via Telegram bot
- Gemini Vision AI for OCR
- Multi-photo support for long receipts
- Neon PostgreSQL storage
- MotherDuck analytics warehouse
- ETL pipeline (Neon → MotherDuck)
- Analytics dashboard with:
  - Spending summary
  - Category breakdown (pie + bar charts)
  - Monthly trends (line chart)
  - Top stores
  - Recent receipts

#### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **Database**: Neon PostgreSQL
- **Analytics**: MotherDuck (DuckDB)
- **AI**: Google Gemini Vision
- **Deployment**: Render (backend) + Netlify (frontend)

#### Initial Components
- Camera component with scroll capture
- Receipt display with categorization
- Analytics dashboard
- API service layer

---

## Version Comparison

| Feature | v1.0.0 | v1.1.0 |
|---------|--------|--------|
| Receipt Scanning | ✅ | ✅ |
| Basic Analytics | ✅ | ✅ |
| Quantity Analytics | ❌ | ✅ |
| Bulk Purchase Insights | ❌ | ✅ |
| Unit Price Tracking | ❌ | ✅ |
| Price Savings Calc | ❌ | ✅ |
| Quantity Trends | ❌ | ✅ |
| Tab Navigation | ❌ | ✅ |
| Euro Currency | ❌ | ✅ |

---

## Links

- **Repository**: https://github.com/trp86/receipts-app
- **Frontend**: https://app-receiptscan.netlify.app
- **Backend**: https://receipts-app-v1co.onrender.com
- **Issues**: https://github.com/trp86/receipts-app/issues

---

## Credits

**Built with**: Claude Code  
**License**: MIT
