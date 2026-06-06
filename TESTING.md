# 🧪 Backend Testing Guide

This guide walks through testing the new backend changes:
- ✅ Telegram removed
- ✅ Category classification added
- ✅ Neon schema updated
- ✅ MotherDuck star schema created
- ✅ ETL job ready

---

## Prerequisites

1. Backend dependencies installed:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Environment variables set in `.env`:
   ```
   DATABASE_URL=postgresql://...
   GOOGLE_API_KEY=...
   MOTHERDUCK_TOKEN=... (optional, will use local DuckDB if not set)
   ```

3. Database schema migrated:
   ```bash
   python -c "from db_service import init_database; init_database()"
   ```

4. Star schema initialized:
   ```bash
   python -c "from motherduck_service import init_star_schema; init_star_schema()"
   ```

---

## Test 1: Check Database Schema ✅

Verify the new columns were added:

```bash
cd backend
python test_database.py
```

**Expected output:**
```
=== Database Test ===
--------------------------------------------------
Total receipts: X
Recent receipts: ...
Unsynced receipts: X
--------------------------------------------------
✓ Database test complete
```

---

## Test 2: Upload Receipt with Categories 📸

**Option A: Using test script**

```bash
cd backend
python test_upload.py path/to/your/receipt.jpg
```

**Expected output:**
```
Testing upload with image: receipt.jpg
User ID: test_user_123
--------------------------------------------------
✓ Image loaded: XXXXX bytes
Uploading to http://localhost:8000/api/upload...
✓ Upload successful!
--------------------------------------------------
Response:
  Receipt ID: 123
  Success: True

Data:
  Store: REWE
  Date: 2026-06-06
  Total: €25.50

  Items (5):
    - Gouda Käse: €3.99 [Dairy Products/Cheese]
    - Bio Milch: €1.29 [Dairy Products/Milk]
    - Tomate: €2.50 [Fruits & Vegetables/Fresh Vegetables]
    - Brot: €1.99 [Bakery/Bread]
    - Wasser: €0.89 [Beverages/Water]
```

**Option B: Using frontend**

1. Start frontend: `cd frontend && npm run dev`
2. Open http://localhost:5173
3. Upload a receipt image
4. Check that categories are returned

**Option C: Using curl**

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@receipt.jpg" \
  -F "user_id=test_user_123"
```

---

## Test 3: Verify Categories in Database 🏷️

```bash
cd backend
python test_database.py
```

Check the output - you should see:
```
Example: Gouda Käse -> Dairy Products/Cheese
```

This confirms Gemini is categorizing items correctly!

---

## Test 4: Run ETL Job 🔄

Sync receipts from Neon to MotherDuck:

```bash
cd backend
python etl_job.py
```

**Expected output:**
```
🚀 Starting ETL Job: Neon → MotherDuck
--------------------------------------------------
=== Starting ETL Job ===
Fetching unsynced receipts from Neon
Found 3 unsynced receipts
✓ Receipt 1 synced (1/3)
✓ Receipt 2 synced (2/3)
✓ Receipt 3 synced (3/3)
=== ETL Complete: 3/3 receipts synced ===
--------------------------------------------------
✅ ETL Complete: 3 receipts synced
```

---

## Test 5: Verify Star Schema in MotherDuck 📊

```bash
cd backend
python -c "
import duckdb
conn = duckdb.connect('receipts_analytics.duckdb')

print('=== Star Schema Test ===')
print()

# Check fact table
print('Fact Receipts:')
print(conn.execute('SELECT COUNT(*) as count FROM fact_receipts').fetchone())
print()

# Check dimensions
print('Categories:')
print(conn.execute('SELECT * FROM dim_categories').fetchall())
print()

# Check items with categories
print('Sample Items with Categories:')
result = conn.execute('''
    SELECT item_name, category, subcategory, total_price
    FROM dim_items
    LIMIT 5
''').fetchall()

for row in result:
    print(f'  {row[0]}: {row[1]}/{row[2]} - €{row[3]}')

conn.close()
"
```

**Expected output:**
```
=== Star Schema Test ===

Fact Receipts:
(3,)

Categories:
[(1, 'Dairy Products', 'Food'), ...]

Sample Items with Categories:
  Gouda Käse: Dairy Products/Cheese - €3.99
  Bio Milch: Dairy Products/Milk - €1.29
  Tomate: Fruits & Vegetables/Fresh Vegetables - €2.50
  ...
```

---

## Test 6: Check Sync Status ✔️

After running ETL, verify receipts are marked as synced:

```bash
cd backend
python test_database.py
```

Look for:
```
Synced to DWH: True
Unsynced receipts: 0
```

---

## Troubleshooting 🔧

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <PID> /F

# Restart
cd backend
uvicorn main:app --reload
```

### Database migration errors
```bash
# Check database connection
python -c "from db_service import get_connection; get_connection(); print('✓ Connected')"

# Re-run migration
python -c "from db_service import init_database; init_database()"
```

### DuckDB file locked
```bash
# Close all Python processes
taskkill /IM python.exe /F

# Delete and recreate
rm receipts_analytics.duckdb
python -c "from motherduck_service import init_star_schema; init_star_schema()"
```

### Categories not showing
- Check Gemini API key is set
- Verify `parser_service.py` was updated with category prompt
- Check raw_json in database has category fields

---

## Success Criteria ✅

All tests pass if:

1. ✅ Database has `user_id`, `synced_to_dwh`, `synced_at` columns
2. ✅ Receipt upload returns items with `category` and `subcategory`
3. ✅ Database stores raw_json with category information
4. ✅ ETL job syncs receipts to MotherDuck
5. ✅ Star schema has data in fact_receipts and dim_items
6. ✅ dim_items includes category/subcategory for each item
7. ✅ Receipts are marked as `synced_to_dwh = TRUE` after ETL

---

## Quick Test Checklist

```bash
# 1. Start backend
cd backend && uvicorn main:app --reload &

# 2. Check health
curl http://localhost:8000/

# 3. Upload test receipt
python test_upload.py receipt.jpg

# 4. Check database
python test_database.py

# 5. Run ETL
python etl_job.py

# 6. Verify sync
python test_database.py
```

All green? Ready for analytics! 🎉
