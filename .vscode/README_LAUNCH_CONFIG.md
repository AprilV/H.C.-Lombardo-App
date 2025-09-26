# 🚀 H.C. Lombardo App - VSCode Launch Configuration

## 📋 **VSCode Launch Configurations**

The H.C. Lombardo App now includes comprehensive VSCode launch configurations for easy development and debugging.

---

## 🎯 **Available Launch Configurations**

### 1. **H.C. Lombardo FastAPI - Template App** (Recommended)
- **Port**: 8001
- **Features**: Jinja2 templates, NFL & Text Analysis pages
- **URL**: http://127.0.0.1:8001

### 2. **H.C. Lombardo FastAPI - NFL Betting API**
- **Port**: 8002  
- **Features**: NFL betting predictions, database operations
- **URL**: http://127.0.0.1:8002

### 3. **H.C. Lombardo FastAPI - Text Classification API**
- **Port**: 8003
- **Features**: Text analysis, sentiment classification
- **URL**: http://127.0.0.1:8003

### 4. **H.C. Lombardo - All APIs (Compound)**
- **Multiple ports**: 8001, 8002, 8003
- **Features**: Starts all APIs simultaneously

---

## ⚡ **Quick Start in VSCode**

### **Method 1: Using Debug Panel**
1. Open **Debug Panel** (`Ctrl+Shift+D`)
2. Select **"H.C. Lombardo FastAPI - Template App"**
3. Click **▶️ Start Debugging** (F5)
4. Open: http://127.0.0.1:8001

### **Method 2: Using Command Palette**
1. Press `Ctrl+Shift+P`
2. Type: **"Tasks: Run Task"**
3. Select: **"H.C. Lombardo - Start Template App"**
4. Open: http://127.0.0.1:8001

---

## 💻 **Manual Terminal Commands**

If you prefer to run the APIs manually from the terminal, use these commands:

### **Primary H.C. Lombardo Template App** (Port 8001)
```bash
# Navigate to project root
cd "c:\IS330\H.C. Lombardo App"

# Start Template App with live reload
python -m uvicorn apis.fastapi_template_inheritance:app --host 127.0.0.1 --port 8001 --reload

# Alternative using full Python path
C:/Users/april/AppData/Local/Microsoft/WindowsApps/python3.11.exe -m uvicorn apis.fastapi_template_inheritance:app --host 127.0.0.1 --port 8001 --reload
```

### **NFL Betting API** (Port 8002)
```bash
# Navigate to project root
cd "c:\IS330\H.C. Lombardo App"

# Start NFL API with live reload
python -m uvicorn apis.nfl_betting_api:app --host 127.0.0.1 --port 8002 --reload
```

### **Text Classification API** (Port 8003)
```bash
# Navigate to project root
cd "c:\IS330\H.C. Lombardo App"

# Start Text API with live reload
python -m uvicorn apis.text_classification_api:app --host 127.0.0.1 --port 8003 --reload
```

### **Test All APIs**
```bash
# Navigate to project root
cd "c:\IS330\H.C. Lombardo App"

# Run comprehensive API tests
python apis/test_hc_lombardo.py
```

---

## 🌐 **URLs After Starting**

### **Template App (Primary)** - Port 8001
- **🏠 Homepage**: http://127.0.0.1:8001
- **🏈 NFL Section**: http://127.0.0.1:8001
- **🤖 Text Section**: http://127.0.0.1:8001/text-classifier
- **📚 API Docs**: http://127.0.0.1:8001/docs
- **📖 ReDoc**: http://127.0.0.1:8001/redoc

### **NFL Betting API** - Port 8002  
- **🏠 Homepage**: http://127.0.0.1:8002
- **📚 API Docs**: http://127.0.0.1:8002/docs
- **🏈 Predictions**: http://127.0.0.1:8002/predict

### **Text Classification API** - Port 8003
- **🏠 Homepage**: http://127.0.0.1:8003  
- **📚 API Docs**: http://127.0.0.1:8003/docs
- **🤖 Classification**: http://127.0.0.1:8003/classify

---

## 🔧 **Configuration Details**

### **Launch Configuration Features**
- ✅ **Live Reload**: Code changes automatically refresh
- ✅ **Debug Support**: Full debugging with breakpoints
- ✅ **Host**: 127.0.0.1 (localhost)
- ✅ **Multiple Ports**: No conflicts between APIs
- ✅ **Environment**: PYTHONPATH configured
- ✅ **Console**: Integrated terminal output

### **Module Paths**
- **Template App**: `apis.fastapi_template_inheritance:app`
- **NFL API**: `apis.nfl_betting_api:app`
- **Text API**: `apis.text_classification_api:app`

---

## 🎯 **Recommended Development Workflow**

1. **Start Primary App**: Use "H.C. Lombardo FastAPI - Template App"
2. **Open Browser**: Visit http://127.0.0.1:8001
3. **Make Changes**: Edit templates or API code
4. **Auto Reload**: Changes appear immediately
5. **Debug**: Set breakpoints in VSCode as needed

---

## 📊 **Port Assignment**

| Service | Port | Status |
|---------|------|--------|
| **Template App** | 8001 | ✅ Primary |
| **NFL Betting API** | 8002 | ✅ Available |
| **Text Classification API** | 8003 | ✅ Available |
| **All APIs (Compound)** | Multiple | ✅ Parallel |

---

## 🎉 **Ready to Launch!**

Your H.C. Lombardo App is now ready with professional VSCode launch configurations:

- 🚀 **Easy debugging** with F5
- ⚡ **Live reload** for rapid development
- 🌐 **Multiple APIs** on separate ports
- 🧩 **Template inheritance** system ready

**Press F5 to start developing!** 🎯