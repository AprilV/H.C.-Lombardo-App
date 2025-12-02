# H.C. Lombardo App - PWA Deployment Guide

## Overview
Deploy your app online to enable PWA installation on any device.

---

## Deployment Steps

### 1. Choose a Hosting Provider

**Recommended: Vercel (Easiest)**
- FREE tier
- Auto-deployment from GitHub
- HTTPS automatic
- Custom domain support
- Perfect for React + Flask apps

**Alternatives:**
- Railway (full-stack with PostgreSQL)
- Render (full-stack with PostgreSQL)
- Netlify (frontend only)

---

### 2. Deploy with Vercel

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy from project folder
cd "c:\IS330\H.C Lombardo App"
vercel
```

Follow the prompts:
- Link to your GitHub account
- Select your project
- Configure build settings
- Deploy!

---

### 3. Connect Your Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain (e.g., hclombardo.com)
3. Update DNS records at your domain registrar:
   - Add CNAME record pointing to Vercel
4. Wait for DNS propagation (5-30 minutes)
5. Vercel automatically provisions SSL/HTTPS

---

### 4. Auto-Deployment Setup

Once connected to GitHub:
- **Push to GitHub** → Vercel automatically rebuilds and deploys
- Every commit triggers a new deployment
- Preview deployments for pull requests
- Production deployment on main branch

**Workflow:**
```bash
git add .
git commit -m "Update feature"
git push origin master
# Vercel automatically deploys in ~2 minutes
```

---

## PWA Installation (After Deployment)

### Desktop (Chrome/Edge/Brave)
1. Visit your site: https://yourdomain.com
2. Look for install icon (⊕) in address bar
3. Click "Install H.C. Lombardo"
4. App appears in Start Menu/Applications
5. Opens in standalone window (no browser UI)

### Mobile (Android)
1. Visit site in Chrome
2. Tap menu (⋮) → "Add to Home Screen"
3. App icon appears on home screen
4. Opens like native app

### Mobile (iOS)
1. Visit site in Safari
2. Tap Share button
3. "Add to Home Screen"
4. App icon appears with other apps

---

## What's Already Configured

Your app has PWA files ready:

```
frontend/public/
├── manifest.json        ✅ PWA manifest configured
├── logo192.png          ✅ App icon (192x192)
├── logo512.png          ✅ App icon (512x512)
└── index.html           ✅ PWA meta tags

frontend/src/
└── serviceWorker.js     ✅ Offline caching
```

No additional PWA setup needed!

---

## Database Deployment

### Option 1: Use Hosting Provider's Database
- Railway/Render include PostgreSQL
- Migrate your data to their database
- Update connection string in environment variables

### Option 2: External Database Service
- ElephantSQL (FREE tier)
- Supabase (FREE tier)
- AWS RDS (paid)

---

## Environment Variables

Set these in your hosting provider:

```
DB_PASSWORD=your_database_password
DATABASE_URL=postgresql://user:pass@host:5432/dbname
NODE_ENV=production
```

---

## Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Database data exported/backed up
- [ ] Environment variables documented
- [ ] Custom domain DNS ready
- [ ] Test locally one final time
- [ ] Create production build succeeds

---

## Cost Estimate

**Free Tier (Perfect for 1 user):**
- Vercel: FREE
- Database (ElephantSQL/Supabase): FREE
- Custom domain: Already own
- SSL/HTTPS: FREE (automatic)

**Total: $0/month** ✅

---

## Support Links

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- PWA Guide: https://web.dev/progressive-web-apps/

---

**Ready to deploy when you are!** 🚀
