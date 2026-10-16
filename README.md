# Anaya Elegance - Free AI Backend

Python (Flask) backend that powers AI Virtual Try-On (IDM-VTON).
Skin Analysis calls Gemini Flash directly from the browser (no server needed).
The 360-degree Spin and AR Wall Preview features are 100 percent frontend - zero backend.

## Cost
- Render free tier web service - /month, sleeps after 15 min inactivity, wakes on request (~30s cold start).
- Hugging Face Spaces (CPU) - /month, community IDM-VTON demo used by default.
- Supabase already on free tier (see /supabase/schema.sql).

## Local dev
    cd backend
    pip install -r requirements.txt
    python app.py            serves http://localhost:8080

## Deploy to Render (free) - 4 steps
1. Create a free account at https://render.com.
2. New+ -> Web Service -> connect this repo (or upload this folder).
3. Render detects Python. Set:
   - Build command: pip install -r requirements.txt
   - Start command: gunicorn app:app --bind 0.0.0.0:
   - Environment: PORT=10000 (Render sets this anyway), TRYON_MODE=gradio,
     GRADIO_SPACE_URL=https://yisol-idm-vton.hf.space
4. Deploy. Render gives a URL like https://anaya-tryon.onrender.com.
5. In frontend open src/lib/config.js and set:
   TRYON_ENDPOINT: 'https://anaya-tryon.onrender.com',
6. Rebuild (npm run build) and redeploy the static site.

## How the try-on works (free path)
- app.py calls the free community IDM-VTON demo on Hugging Face Spaces via gradio_client (no API key needed).
- Customer selfies sent from browser as base64 -> converted to temp files on the server -> passed to the Space -> returned as base64.
- Limitation: community Spaces have rate limits and can be rebuilt/moved by their authors. If it breaks,
  search HF Spaces for 'IDM-VTON' and update GRADIO_SPACE_URL, or set TRYON_MODE=local and run on your own GPU.

## Faster / higher quality (optional, paid GPU)
- Replicate (pay-per-run): switch to their IDM-VTON model - usually a few cents per try-on.
- Runpod / Modal self-host IDM-VTON (needs an NVIDIA GPU, ~.40/hr).

## 360-degree spin - zero backend
- From admin: Edit Product -> 360-degree Spin - one image URL per line (12-24).
- The viewer (src/components/Spin360.jsx) is pure React: drag/swipe rotates, lazy-loads +/- 2 frames, auto-rotates until touched.
- Photo tips: white/neutral backdrop, tripod, turntable, consistent lighting, 15 degree increments (24 photos).

## AR Wall Preview - zero backend
- Use a free photo editor (Photopea / GIMP) to remove background -> save as transparent PNG.
- Paste PNG URL in admin -> AR Wall Preview - transparent PNG URL -> Save Product.
- Viewer (src/components/ARViewer.jsx) opens rear camera, overlays the PNG, supports drag-move, pinch/scroll-scale, rotate, reset.
  No 8th Wall (paid) required. True markerless wall tracking (WebXR hit-test) is still experimental;
  this camera-overlay approach works on 99 percent of phones today.

## Skin Analysis - zero backend (Gemini free tier)
1. Create a free API key at https://aistudio.google.com/apikey
2. In src/lib/config.js set GEMINI_API_KEY: '...'
3. Rebuild + redeploy - analysis runs directly from https://generativelanguage.googleapis.com.
4. Gemini's free tier covers well above typical store traffic. If exceeded, add caching or your own proxy later.

## Free-tier caveats
- Render free services sleep after 15 min of inactivity (first request wakes them, ~30s cold start).
- Hugging Face spaces can be rebuilt by their authors at any time.
- Supabase free projects pause after 7 days of inactivity; activity from the app keeps them awake.
- Gemini free has a generous daily quota; cache results if you exceed it.
