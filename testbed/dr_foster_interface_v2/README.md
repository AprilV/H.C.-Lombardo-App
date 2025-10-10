# 🏈 H.C. Lombardo Interactive 3D Dashboard (v2)

**Student:** April V. Sykes  
**Course:** IS330  
**Date:** October 10, 2025

---

## 🎯 Overview

This is an advanced interactive 3D dashboard showcasing the H.C. Lombardo NFL Analytics Platform architecture, assignments, and technical implementations. Built with THREE.js for 3D visualization and modern web technologies.

## 🌟 Features

### **3D Network Visualization**
- **Interactive Architecture Diagram** - Explore 5 interconnected components:
  - 💻 React Frontend (Client Tier)
  - 🌐 Flask API Server (Application Tier)
  - 🗄️ PostgreSQL Database (Data Tier)
  - ☁️ ESPN Cloud API (External Data Source)
  - 📡 API Status Monitor (Live Health Tracking)

### **Dynamic Real-Time Features**
- **🔴🟢 Live API Status Monitoring** - 3D tower changes color based on server status:
  - **Red** = API server offline (static data mode)
  - **Green** = API server online (live data mode)
- **⏰ Auto-Updating Date/Time** - Header displays current date and live clock (updates every second)
- **🔄 Data Mode Indicator** - Floating badge shows LIVE or STATIC status
- **📊 Live Stats** - Dashboard metrics update from API or cached data

### **7 Comprehensive Tabs**
1. **📖 Overview** - Project introduction, architecture summary, quick links
2. **🏗️ Week 1-2** - ML model development, SQLite database, initial prototypes
3. **🚀 Weeks 2-4** - React frontend, PostgreSQL migration, DHCP port management
4. **🗄️ Database** - PostgreSQL schema, 15+ tables, data relationships
5. **🏛️ 3D Architecture** - Interactive visualization of three-tier design
6. **✅ Testing** - Q&A section with technical implementation details
7. **💻 GitHub** - Repository information and quick access links

### **Professional Design**
- **Dark Theme** - Easy on the eyes with professional color scheme
- **Responsive Layout** - Works on all screen sizes
- **90% Zoom Optimized** - Perfect viewing at 90% browser zoom
- **Smooth Animations** - Rotating 3D objects, pulsing connections, interactive hover effects
- **Chart.js Integration** - Beautiful data visualizations

---

## 🚀 How to Open

### Method 1: From VS Code
1. Navigate to `testbed/dr_foster_interface_v2/` in Explorer
2. Right-click `index.html`
3. Select "Reveal in File Explorer"
4. Double-click the file to open in your default browser

### Method 2: Direct Path
Navigate to:
```
C:\IS330\H.C Lombardo App\testbed\dr_foster_interface_v2\index.html
```
Double-click to open.

### Method 3: Terminal
```powershell
cd "c:\IS330\H.C Lombardo App\testbed\dr_foster_interface_v2"
explorer index.html
```

---

## 🔧 Technical Stack

### Frontend Technologies
- **THREE.js r128** - 3D graphics and visualization
- **Chart.js 4.4** - Data charts and graphs
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with gradients and animations
- **HTML5** - Semantic markup

### API Integration
- **Flask REST API** - Backend server (Port 5000)
- **Fetch API** - Asynchronous data loading
- **CORS** - Cross-origin resource sharing
- **Error Handling** - Graceful fallback to static data

### Data Modes
1. **Live Mode** - Connects to Flask API at `http://localhost:5000/api/teams/count`
2. **Static Mode** - Uses cached data when API is unavailable
3. **Auto-Refresh** - Updates every 5 minutes in live mode

---

## 📊 Dashboard Statistics (Static Data)

- **32 NFL Teams** tracked
- **272 Regular Season Games** analyzed
- **96.8% Prediction Accuracy** achieved
- **15+ Database Tables** implemented

---

## 🎨 3D Architecture Components

### Frontend (Client Tier)
- Position: Left side of visualization
- Color: Professional Blue (#4a90e2)
- Represents: React SPA on Port 3000

### API Server (Application Tier)
- Position: Center of visualization
- Color: Professional Gray (#5a6c7d)
- Represents: Flask REST API on Port 5000

### Database (Data Tier)
- Position: Right side of visualization
- Color: Professional Teal (#2a9d8f)
- Represents: PostgreSQL 18 database

### ESPN API (External Source)
- Position: Upper right
- Color: Light Blue (#7fb3d5)
- Represents: Cloud-based sports data

### API Monitor (Health Tracker)
- Position: Lower center
- Color: **Dynamic** - Red (offline) or Green (online)
- Represents: Live system health monitoring

---

## 🔄 Dynamic Color System

### API Status Tower
The 3D monitoring tower provides real-time visual feedback:

**Offline State (Red):**
- Tower Body: `#e63946` (Red/Orange)
- Status LED: `#ff4444` (Bright Red)
- Edge Lines: `#ff8fa3` (Light Red)
- Badge: "📊 Static Data" (Blue)

**Online State (Green):**
- Tower Body: `#50c878` (Professional Green)
- Status LED: `#44ff44` (Bright Green)
- Edge Lines: `#8fff8f` (Light Green)
- Badge: "🟢 Live Data" (Green)

Colors update automatically when:
- Dashboard initializes
- API connection status changes
- Auto-refresh cycle runs (every 5 minutes)

---

## 📝 File Structure

```
dr_foster_interface_v2/
├── index.html              # Main dashboard (2,164 lines)
├── README.md              # This file
├── DEMO_SCRIPT.md         # Presentation guide
├── DEPLOYMENT_SUMMARY.md  # Deployment instructions
├── FINAL_REPORT.md        # Project completion report
├── IMPLEMENTATION_COMPLETE.md
├── LIVE_DATA_GUIDE.md     # API integration guide
├── TESTING_CHECKLIST.md   # QA checklist
└── VISUAL_REPRESENTATIONS.md
```

---

## ✅ Testing Checklist

### Visual Tests
- [x] All 7 tabs load without errors
- [x] 3D visualization renders correctly
- [x] API Status tower displays properly
- [x] Date/time auto-updates every second
- [x] Navigation works smoothly
- [x] 90% zoom displays perfectly

### Functional Tests
- [x] Static data mode works (API offline)
- [x] Live data mode works (API online)
- [x] Status badge reflects correct mode
- [x] Tower color matches API status
- [x] No console errors
- [x] Auto-refresh functions properly

### Browser Compatibility
- [x] Chrome/Edge (Recommended)
- [x] Firefox
- [x] Safari (MacOS)

---

## 🎯 Recommended Browser Settings

For optimal viewing experience:
- **Browser Zoom:** 90%
- **Screen Resolution:** 1920x1080 or higher
- **JavaScript:** Enabled
- **WebGL:** Enabled (for 3D graphics)

---

## 🔗 Quick Links

- **GitHub Repository:** https://github.com/AprilV/H.C.-Lombardo-App
- **Flask API:** http://localhost:5000/api/teams/count
- **React Frontend:** http://localhost:3000 (when running)

---

## 📅 Version History

### Version 2.0 (October 9-10, 2025)
**October 9, 2025:**
- ✅ Built initial 3D interactive dashboard with THREE.js
- ✅ Created 7-tab navigation system (Overview, Week 1-2, Weeks 2-4, Database, Architecture, Testing, GitHub)
- ✅ Implemented 3D network architecture visualization with 5 components
- ✅ Added static/live data mode support
- ✅ Integrated Chart.js data visualizations
- ✅ Completed cleanup and final testing phase
- ✅ Fixed code quality issues (removed debug statements, TODOs)

**October 10, 2025:**
- ✅ Added dynamic 3D tower color changes based on API status (red=offline, green=online)
- ✅ Implemented auto-updating date/time in header with live clock
- ✅ Updated student name to "April V. Sykes"
- ✅ Fixed THREE.js material errors (removed invalid emissive properties from MeshBasicMaterial)
- ✅ Enhanced API status monitoring with real-time visual feedback
- ✅ Updated all documentation files (README.md files, dashboard content)

### Version 1.0 (October 8-9, 2025)
- ✅ Initial development and prototyping
- ✅ Basic HTML structure and styling
- ✅ Content migration from previous dashboard versions

---

## 👩‍💻 Developer

**April V. Sykes**  
IS330 - AI Development Environment  
Dr. Foster

---

## 📄 License

Educational project for IS330 coursework.

---

**Last Updated:** October 10, 2025  
**Dashboard Version:** 2.0  
**Status:** ✅ Production Ready
