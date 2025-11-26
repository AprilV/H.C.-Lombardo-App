# Deploy to Railway.app

## Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (free - $5 credit/month)

## Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `H.C.-Lombardo-App` repository
4. Railway will auto-detect Python app

## Step 3: Add PostgreSQL Database
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway creates database automatically
4. Click on PostgreSQL service → "Variables" tab
5. Copy these connection details (you'll need them)

## Step 4: Set Environment Variables
Click on your web service → "Variables" tab → Add these:

```
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
PYTHON_VERSION=3.10.0
```

**Important:** Railway uses `${{Postgres.VARIABLE}}` syntax to auto-reference the database

## Step 5: Deploy
1. Railway auto-deploys from GitHub
2. Every git push triggers new deployment
3. Check logs to see build progress

## Step 6: Get Your URL
1. Click on web service → "Settings"
2. Scroll to "Domains"
3. Click "Generate Domain"
4. Your app will be at: `https://your-app-name.up.railway.app`

## Step 7: Populate Database
Once deployed, run locally:
```powershell
python populate_render_with_live_data.py
```
Paste the DATABASE_URL from Railway (found in Postgres → Variables → DATABASE_URL)

## Advantages over Render:
- ✅ Database never expires (as long as you have credit)
- ✅ $5/month free credit (enough for small apps)
- ✅ More reliable builds
- ✅ Better logging
- ✅ Easier database connections
- ✅ Auto-deployments work better

## Cost:
- Free: $5 credit/month
- Your app will likely use $3-4/month
- Database included in credit
- No surprise charges (pauses when credit runs out)
