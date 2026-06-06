# Deployment Guide

## Phase 7: Web App Deployment

### Architecture

```
User (Mobile Browser)
    ↓
React Frontend (PWA)
    ↓ HTTP POST /api/upload
FastAPI Backend
    ↓
Gemini Vision API
    ↓
Neon PostgreSQL
```

## Backend Deployment (Render)

### 1. Prepare Backend

Already configured in `backend/main.py`:
- `/api/upload` endpoint
- CORS middleware
- File upload support

### 2. Environment Variables

Set in Render dashboard:
```
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
NEON_DATABASE_URL=postgresql://...
```

### 3. Deploy Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Update CORS Origins

After deployment, update `main.py` with production frontend URL:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-frontend-domain.com"
]
```

## Frontend Deployment

### Option 1: Netlify (Recommended)

1. **Build**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy**
   - Connect GitHub repo to Netlify
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Environment variable: `VITE_API_URL=https://your-backend.onrender.com`

3. **Configure**
   - Add `_redirects` file in `public/`:
     ```
     /*    /index.html   200
     ```

### Option 2: Vercel

1. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

2. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

### Option 3: GitHub Pages

1. **Build**
   ```bash
   npm run build
   ```

2. **Deploy**
   ```bash
   npm install -g gh-pages
   gh-pages -d dist
   ```

## Post-Deployment

### 1. Update Backend CORS

Add production frontend URL to allowed origins.

### 2. Test Upload Endpoint

```bash
curl -X POST https://your-backend.onrender.com/api/upload \
  -F "file=@test.jpg"
```

### 3. Mobile Testing

- Access frontend URL on mobile device
- Grant camera permissions
- Test full flow

## Production Considerations

### Security
- Add rate limiting
- Implement authentication
- Validate file types/sizes
- Use HTTPS only

### Performance
- Add CDN for static assets
- Implement image compression
- Cache API responses
- Use connection pooling for DB

### Monitoring
- Add logging service (e.g., Sentry)
- Monitor API response times
- Track error rates
- Set up uptime monitoring

## Cost Estimates (Free Tier)

- **Render**: Free tier (sleeps after inactivity)
- **Netlify**: 100GB bandwidth/month free
- **Neon PostgreSQL**: 0.5GB storage free
- **Gemini API**: Free tier available

## Troubleshooting

### CORS Errors
- Verify backend CORS origins include frontend URL
- Check for HTTPS/HTTP mismatch

### Camera Not Working
- Ensure HTTPS (required for camera access)
- Check browser camera permissions

### Upload Fails
- Verify backend endpoint is accessible
- Check file size limits
- Review backend logs
