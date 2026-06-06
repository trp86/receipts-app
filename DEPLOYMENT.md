# 🚀 Deployment Guide - MotherDuck Analytics

## Quick Start

1. Get MotherDuck token → Add to Render
2. Push code (done ✅)
3. Initialize star schema
4. Run ETL to sync receipts
5. Test!

---

## Step 1: Get MotherDuck Token

1. Go to https://app.motherduck.com/
2. Click profile → Settings → Access Tokens
3. Create Token → Copy it

---

## Step 2: Add to Render

1. https://dashboard.render.com/ → receipts-app-v1co
2. Environment tab
3. Add: MOTHERDUCK_TOKEN = <your_token>
4. Save (auto-redeploys)

---

## Step 3: Verify Deployment

```bash
curl https://receipts-app-v1co.onrender.com/api/health
```

Should show motherduck: token_configured

---

## Step 4: Initialize Star Schema

```bash
curl -X POST https://receipts-app-v1co.onrender.com/api/admin/init-star-schema
```

---

## Step 5: Sync Existing Receipts

```bash
curl -X POST https://receipts-app-v1co.onrender.com/api/admin/run-etl
```

---

## Done! Test upload with categories

```bash
curl -X POST https://receipts-app-v1co.onrender.com/api/upload \
  -F "file=@receipt.jpg" -F "user_id=test"
```

Check response has category/subcategory fields!
