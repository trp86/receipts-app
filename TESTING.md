# Testing Guide

## End-to-End Testing

### Prerequisites

1. Backend running on http://localhost:8000
2. Frontend running on http://localhost:5173
3. Camera access granted in browser

### Backend Setup

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/
# Expected: {"message":"Receipt Processing Backend"}
```

### Frontend Setup

```bash
cd frontend
npm run dev
```

Open browser: http://localhost:5173

### Manual Test Flow

1. **Camera Permission**
   - Open app in browser
   - Click "Allow" when prompted for camera access
   - Verify camera preview appears

2. **Capture Receipt**
   - Point camera at receipt
   - Click "📸 Capture Receipt"
   - Verify preview shows captured image

3. **Process Receipt**
   - Click "✓ Process Receipt"
   - Wait for "Processing receipt..." message
   - Verify API call to backend

4. **View Results**
   - Check parsed receipt data displays:
     - Store name
     - Date
     - Total amount
     - Item list
   - Click "📸 Scan New Receipt" to restart

### Testing with Telegram

Backend also supports Telegram webhook at `/webhook` endpoint.

### Error Scenarios

1. **Camera Denied**: Shows error message
2. **Backend Offline**: Shows "Failed to process receipt"
3. **Invalid Image**: Backend returns error response

### API Test

Test upload endpoint directly:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_receipt.jpg"
```

Expected response:
```json
{
  "success": true,
  "receipt_id": 1,
  "data": {
    "store_name": "...",
    "date": "...",
    "total_amount": "...",
    "items": [...]
  }
}
```

## Mobile Testing

### Option 1: Local Network
1. Find your local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Update frontend `.env`: `VITE_API_URL=http://YOUR_IP:8000`
3. Update backend CORS: add your IP to allowed origins
4. Access from mobile: `http://YOUR_IP:5173`

### Option 2: ngrok
```bash
ngrok http 5173
```

Use the ngrok URL on mobile device.

## Known Issues

- Camera may not work in non-HTTPS context on some mobile browsers
- First load may be slower due to Gemini API initialization
