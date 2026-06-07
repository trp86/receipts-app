# Deploy Frontend to Netlify

## Option 1: Drag and Drop (Fastest)

1. Open: https://app.netlify.com/sites/app-receiptscan/deploys
2. Drag the `dist` folder to the deploy area
3. Wait ~30 seconds

## Option 2: Netlify CLI

```bash
cd frontend
netlify login
netlify deploy --prod --dir=dist
```

## Option 3: GitHub Auto-Deploy

If you have GitHub integration enabled, Netlify will auto-deploy when you push to main.

Check status: https://app.netlify.com/sites/app-receiptscan/deploys
