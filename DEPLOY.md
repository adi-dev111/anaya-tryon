# AI Try-On Backend - simple deployment

You only need one public URL at the end.

## Confusions (answered simply)
- Render will not make you open a Google account. On render.com you can press "Sign in with GitHub".
- Render detects Python automatically when it sees requirements.txt in your repo.
- Render free services sleep after 15 minutes without requests. This is normal and free. First request may take about 30 seconds to wake up.
- You do NOT need the command line locally. Render builds Python itself.

## Option A: Render free
1. Put the backend folder in a private GitHub repository.
2. Go to render.com -> sign in with GitHub -> New -> Web Service -> choose that repository.
3. Settings:
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
   Environment Variables:
      TRYON_MODE=gradio
      GRADIO_SPACE_URL=https://yisol-idm-vton.hf.space
4. Press Create Web Service.
5. Wait 2 to 4 minutes. Copy the public URL it shows.
6. In anaya-elegance/src/lib/config.js set TRYON_ENDPOINT to that URL.
7. Run npm run build, then drag the dist folder to Netlify again.

## Option B: Hugging Face Spaces free - less manual and no card needed
1. Create a free account at huggingface.co.
2. New Space -> Docker -> name it anaya-tryon -> visibility public.
3. Upload backend/Dockerfile and backend/app.py.
4. Wait for build, then copy the Space page URL.
5. Paste it into config.js -> TRYON_ENDPOINT.

## Important
- If the public IDM-VTON demo is busy or locked, try it later or duplicate the Space in Hugging Face.
- The test button opens only when TRYON_ENDPOINT is filled; otherwise the page tells customers the feature is being configured.
