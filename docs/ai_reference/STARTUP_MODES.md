# H.C. Lombardo - Startup Guide

## Two Startup Modes

### 🔧 **START-DEV.bat** - Development Mode (Recommended for Development)
**Use this when actively coding and making changes**

- **Ports**: React on 3000, Flask on 5000
- **Hot Reload**: ✅ YES - Changes appear instantly (1-2 seconds)
- **Startup Time**: ~20-30 seconds
- **Speed**: Moderate (dev server overhead)
- **Perfect for**:
  - Writing new features
  - Testing UI changes
  - Debugging
  - Active development

**How it works:**
```
React Dev Server → Hot reload → See changes instantly
Flask API → Provides data
```

**To use:**
1. Double-click `START-DEV.bat`
2. Wait 20-30 seconds for compilation
3. Browser opens to `http://localhost:3000`
4. Edit code → Save → See changes in 1-2 seconds!

---

### 🚀 **START.bat** - Production Mode (Recommended for Testing/Demos)
**Use this for final testing, demos, or deployment**

- **Ports**: Everything on 5000 (single server)
- **Hot Reload**: ❌ NO - Must rebuild to see changes
- **Startup Time**: ~30-60 seconds (builds once, then fast)
- **Speed**: FAST (optimized, minified code)
- **Perfect for**:
  - Showing someone the app
  - Testing final performance
  - Production deployment
  - When finished with features

**How it works:**
```
npm run build → Optimized static files → Flask serves everything
```

**To use:**
1. Double-click `START.bat`
2. Wait 30-60 seconds for build
3. Browser opens to `http://localhost:5000`
4. App loads instantly!

**To make changes in production mode:**
1. Run `STOP.bat`
2. Edit your code
3. Run `START.bat` again (rebuilds automatically)

---

## Quick Comparison

| Feature | START-DEV.bat | START.bat |
|---------|---------------|-----------|
| **Ports** | 3000 & 5000 | 5000 only |
| **Hot Reload** | ✅ YES | ❌ NO |
| **Startup** | 20-30 sec | 30-60 sec (first time) |
| **Speed** | Moderate | FAST |
| **File Size** | Large | Small (optimized) |
| **Use Case** | Development | Testing/Production |

---

## Stopping the App

**Both modes:** Run `STOP.bat` to stop all services

---

## Typical Workflow

### While Building Features (Development)
```bash
1. START-DEV.bat      # Start with hot reload
2. Edit code          # Make your changes
3. Save file          # See changes in 1-2 seconds
4. Repeat steps 2-3   # Keep developing
5. STOP.bat           # When done for the day
```

### When Ready to Test/Demo (Production)
```bash
1. STOP.bat           # Stop dev mode if running
2. START.bat          # Build and run production mode
3. Show/test app      # Fast, optimized version
4. STOP.bat           # When done
```

### Making Changes After Production Build
```bash
1. STOP.bat           # Stop production mode
2. START-DEV.bat      # Switch to dev mode for changes
3. Edit & test        # Use hot reload
4. STOP.bat           # Stop dev mode
5. START.bat          # Rebuild production when satisfied
```

---

## Pro Tips

- 💡 **Use START-DEV.bat 90% of the time** - hot reload is your friend!
- 💡 **Use START.bat before showing someone** - looks professional, loads fast
- 💡 **Never run both at the same time** - stop one before starting the other
- 💡 **Production build is required for PWA installation** - START.bat enables app installation

---

## Troubleshooting

**"Can't reach this page"**
- Make sure the correct server is running
- Dev mode: Check `http://localhost:3000`
- Production mode: Check `http://localhost:5000`

**Changes not appearing**
- Dev mode: Check that hot reload is working (should be automatic)
- Production mode: You must run `STOP.bat` then `START.bat` again

**Slow startup**
- Dev mode: 20-30 seconds is normal
- Production mode: First build takes 30-60 seconds, subsequent startups are fast

---

## Summary

🔧 **Developing?** → Use `START-DEV.bat`
🚀 **Showing off?** → Use `START.bat`
🛑 **Done?** → Use `STOP.bat`
