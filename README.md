# Receipt Processing MVP

This project captures receipt images via Telegram bot and processes them using OCR.

## Flow
Telegram → Backend → OCR → JSON → Database → Telegram

## Stack
- FastAPI (backend)
- Render (hosting)
- Neon (database)
- Tesseract OCR

## Goal
Build a simple, cloud-only, free MVP.

---

## Local Development

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run locally
```bash
cd backend
uvicorn main:app --reload
```

### Test webhook
```bash
python test_webhook.py
```

---

## Deployment to Render

### 1. Push to GitHub
Ensure code is in a GitHub repository.

### 2. Create Web Service on Render

1. Go to [render.com](https://render.com) dashboard
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `receipt-processor` (or your choice)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** leave blank
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

5. Click **"Create Web Service"**

### 3. Register Telegram Webhook

After deployment completes, get your Render URL (e.g., `https://receipt-processor.onrender.com`)

Register webhook with Telegram:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-render-url.onrender.com/webhook"
```

Replace:
- `<YOUR_BOT_TOKEN>` with your actual Telegram bot token
- `your-render-url` with your Render deployment URL

### 4. Verify Webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

Should show your webhook URL is registered.

### 5. Test
Send a photo to your Telegram bot. Check Render logs for:
- `Photo detected in message`
- `Extracted chat_id: <id>`
- `Extracted file_id: <file_id>`

---

## Notes

⚠️ **Render Free Tier:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Acceptable for MVP testing

⚠️ **Environment Variables:**
- Add sensitive data (bot token, DB credentials) via Render dashboard
- Navigate to: Environment → Add Environment Variable