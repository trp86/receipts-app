# 🧪 ETL Job Testing Guide

## Test 1: Manual Trigger via GitHub Actions

1. **Go to Actions page:**
   https://github.com/trp86/receipts-app/actions

2. **Select workflow:**
   - Click "ETL Sync - Neon to MotherDuck" in left sidebar

3. **Run manually:**
   - Click "Run workflow" button (top right)
   - Select branch: `main`
   - Click "Run workflow"

4. **Watch it run:**
   - Click on the new workflow run (appears at top)
   - Click "sync-receipts" job
   - Watch logs in real-time

5. **Expected output:**
   ```
   🔄 Triggering ETL sync...
   HTTP Status: 200
   Response: {"success":true,"message":"ETL complete: X receipts synced"}
   ✅ ETL sync completed successfully
   ```

---

## Test 2: Upload New Receipt and Check Auto-Sync

1. **Upload a receipt:**
   - Go to: https://app-receiptscan.netlify.app/
   - Upload a receipt image
   - Verify it processes successfully

2. **Check database state (before sync):**
   ```bash
   curl https://receipts-app-v1co.onrender.com/api/health
   ```
   Look for `receipt_count`

3. **Wait for next hourly sync** (or trigger manually)

4. **Verify sync happened:**
   - Check GitHub Actions run logs
   - Should show "X receipts synced"

---

## Test 3: Check MotherDuck Data

1. **Go to MotherDuck:**
   https://app.motherduck.com/

2. **Select database:**
   - Click on `receipts_analytics`

3. **Run queries:**

   **Check fact table:**
   ```sql
   SELECT COUNT(*) as total_receipts 
   FROM fact_receipts;
   ```

   **Check items with categories:**
   ```sql
   SELECT 
     item_name, 
     category, 
     subcategory, 
     total_price
   FROM dim_items
   LIMIT 10;
   ```

   **Check receipts by store:**
   ```sql
   SELECT 
     s.store_name,
     COUNT(*) as receipt_count,
     SUM(f.total_amount) as total_spent
   FROM fact_receipts f
   JOIN dim_store s ON f.store_key = s.store_key
   GROUP BY s.store_name
   ORDER BY total_spent DESC;
   ```

---

## Test 4: Monitor Scheduled Runs

**Next scheduled run:** Every hour at :00

1. **Check upcoming runs:**
   - Go to: https://github.com/trp86/receipts-app/actions
   - Filter: "ETL Sync - Neon to MotherDuck"
   - You'll see runs every hour

2. **Check logs of recent runs:**
   - Click on any completed run
   - View "sync-receipts" job logs
   - Verify success/failure

---

## Expected Behavior

### When receipts are synced:
```
✅ ETL complete: 4 receipts synced
```

### When no new receipts:
```
✅ ETL complete: 0 receipts synced
```

### When it fails:
```
❌ ETL sync failed
(Check Render logs for details)
```

---

## Monitoring Dashboard

### GitHub Actions:
https://github.com/trp86/receipts-app/actions

### Backend Health:
https://receipts-app-v1co.onrender.com/api/health

### Backend Logs:
https://dashboard.render.com/ → receipts-app-v1co → Logs

### MotherDuck Console:
https://app.motherduck.com/

---

## Troubleshooting

### Workflow doesn't appear:
- Refresh the page
- GitHub Actions may take ~30 seconds to detect new workflows
- Check: Settings → Actions → General → "Allow all actions"

### Workflow fails:
- Check Render backend is running
- Check MotherDuck token is valid
- View detailed logs in workflow run

### No receipts synced:
- Normal if all receipts are already synced
- Upload a new receipt and wait for next run

---

## Success Criteria

✅ Workflow appears in GitHub Actions
✅ Manual trigger works
✅ Workflow runs automatically every hour
✅ Receipts sync successfully
✅ MotherDuck data updates
✅ No errors in logs
