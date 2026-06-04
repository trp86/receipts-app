# Receipt Scanner Frontend

React-based Progressive Web App (PWA) for scanning receipts via mobile camera.

## Features

- 📸 Camera capture with rear camera preference
- 🔍 High-quality image capture (1920x1080)
- 📱 Mobile-responsive design
- ⚡ Fast preview and retake
- 🔄 Real-time processing feedback

## Tech Stack

- React 19
- Vite 5
- react-webcam
- Axios

## Development

```bash
npm install
npm run dev
```

App runs at: http://localhost:5173

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Camera Permissions

The app requires camera permission to function. Users will be prompted on first access.

## Mobile Testing

For best results, test on actual mobile device or use Chrome DevTools device emulation with camera simulation.

## Build

```bash
npm run build
```

Outputs to `dist/` directory.
