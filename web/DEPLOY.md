# Deploying NewsAI Web Frontend

This document explains how to host your `web/index.html` for free.

---

## Option 1 — GitHub Pages (Fastest, Zero Config)

Since your project is already on GitHub (`DarshanRevankar24/newsReader`):

1. Push the `web/` folder to GitHub:
   ```bash
   git add web/
   git commit -m "Add web frontend"
   git push origin main
   ```

2. Go to your repo on GitHub → **Settings** → **Pages**

3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/web`

4. Click **Save**. Your site will be live at:
   ```
   https://darshanrevankar24.github.io/newsReader/
   ```

---

## Option 2 — Netlify (Drag & Drop, 1 Minute)

1. Go to [netlify.com](https://netlify.com) and sign up/log in
2. Drag and drop the `web/` folder onto the Netlify dashboard
3. Done! You get a free `*.netlify.app` URL instantly

---

## Option 3 — Vercel

```bash
npm i -g vercel
cd web
vercel --yes
```

---

## Backend (Already Deployed)

The frontend talks to your existing backend at:
```
https://darshanrevankar-newsai.hf.space
```

CORS is now enabled in `app/main.py`. To redeploy the backend on HuggingFace Spaces:

1. Push the updated `app/main.py` to your HuggingFace Space repo
2. The Space will auto-rebuild

---

## Environment Variables (None needed!)

The web frontend is a plain static HTML file — no environment variables, no build step, no npm install.  
Just open `web/index.html` in a browser or deploy to any static host.
