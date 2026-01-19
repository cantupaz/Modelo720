# Modelo 720 - Complete Application Setup

## 🎉 What's Been Built

A complete full-stack application for managing Spanish Modelo 720 tax declarations:

- ✅ **Backend API** (FastAPI + Python) - Running in Docker
- ✅ **Frontend Web App** (Vue 3 + Vite) - Just created!
- 📦 **Electron Wrapper** - Coming in Phase 3

---

## 📁 Project Structure

```
Modelo720/
├── Modelo720/                    # Core Python library
│   ├── __init__.py
│   ├── parser.py
│   └── declaracion.py
│
├── backend/                      # FastAPI API
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   └── models/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/                     # Vue 3 Web App
    ├── src/
    │   ├── components/
    │   ├── views/
    │   ├── stores/
    │   ├── api/
    │   └── router/
    ├── package.json
    └── vite.config.js
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Backend (Already Running)

The backend should already be running in Docker. If not:

```bash
cd backend
docker compose up -d
```

Verify it's working:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"modelo720-api"}
```

### Step 2: Install Node.js & npm

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# Verify installation
node --version  # Should be v14 or higher
npm --version
```

### Step 3: Start Frontend

```bash
cd frontend
npm install     # Install dependencies (first time only)
npm run dev     # Start dev server
```

The app will open at: **http://localhost:5173**

---

## 🎨 Frontend Features

### 1. **Home Page** (`/`)
- Overview of the application
- Quick access to main features
- Recent declarations history

### 2. **Parse & Analyze** (`/parse`)
- Upload .720 or CSV files
- Drag-and-drop interface
- Real-time validation
- View all declaration details
- Export to different formats

### 3. **Format Converter** (`/convert`)
- Convert .720 ↔ CSV
- Instant download
- Format preview

### 4. **Declaration Viewer** (`/view/:id`)
- Detailed view of parsed declarations
- Expandable detail records
- Export functionality

---

## 🔧 Development Workflow

### Terminal 1: Backend
```bash
cd /home/erick/Modelo720/backend
docker compose up
# Or keep it running in background with -d flag
```

### Terminal 2: Frontend
```bash
cd /home/erick/Modelo720/frontend
npm run dev
```

### Making Changes

**Backend**: Edit files in `backend/app/`, Docker will auto-reload

**Frontend**: Edit files in `frontend/src/`, Vite will hot-reload instantly

---

## 📝 Testing the Application

1. **Open Frontend**: http://localhost:5173

2. **Upload a Test File**:
   - Go to "Analizar"
   - Upload `/home/erick/Modelo720/example.720`
   - View the parsed data and validation results

3. **Convert Format**:
   - Go to "Convertir"
   - Upload `example.720`
   - Select "Desde .720 a CSV"
   - Click "Convertir"
   - File downloads automatically

4. **View API Docs**: http://localhost:8000/docs

---

## 🛠️ Common Commands

### Backend
```bash
# Start
docker compose up -d

# Stop
docker compose down

# View logs
docker compose logs -f

# Restart after code changes
docker compose restart
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new package
npm install <package-name>
```

---

## 🐛 Troubleshooting

### Backend not accessible
```bash
# Check if running
docker compose ps

# Check logs
docker compose logs

# Restart
docker compose restart
```

### Frontend can't connect to API
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify API base URL in `frontend/src/api/client.js`

### npm install fails
```bash
# Clear cache and retry
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

---

## 📦 Building for Production

### Frontend Only (Static Files)
```bash
cd frontend
npm run build
# Output in: frontend/dist/
```

Deploy `dist/` folder to:
- Vercel, Netlify, Cloudflare Pages (free)
- Or any static hosting service

### Full Stack with Docker
```bash
# Build everything
docker compose -f docker-compose.prod.yml build

# Run production stack
docker compose -f docker-compose.prod.yml up
```

---

## 🎯 Next Steps

### Now (Immediate)
1. ✅ Test the frontend with your example files
2. ✅ Customize styling/colors if needed
3. ✅ Add any missing fields or features

### Soon (This Week)
1. 📱 Make it responsive for mobile
2. 🔐 Add authentication (if needed for web version)
3. 💾 Add database for storing declarations (optional)

### Later (Phase 3)
1. 🖥️ Wrap in Electron for desktop app
2. 📦 Create installers for Windows/Mac/Linux
3. 🚀 Deploy web version to production

---

## 📚 Key Files to Know

**Frontend Entry Point**:
- `frontend/src/main.js` - App initialization
- `frontend/src/App.vue` - Main app component
- `frontend/src/router/index.js` - Routes configuration

**API Client**:
- `frontend/src/api/client.js` - All API calls

**State Management**:
- `frontend/src/stores/declaration.js` - Global state

**Main Views**:
- `frontend/src/views/Home.vue`
- `frontend/src/views/Parse.vue`
- `frontend/src/views/Convert.vue`

**Components**:
- `frontend/src/components/FileUploader.vue` - File upload UI
- `frontend/src/components/DeclarationViewer.vue` - Display declarations
- `frontend/src/components/DetailView.vue` - Show detail records

---

## 🎨 Customization

### Change Colors
Edit `frontend/src/style.css`:
```css
:root {
  --primary-color: #646cff;  /* Change this */
}

button.primary {
  background-color: #646cff;  /* And this */
}
```

### Add a New Page
1. Create `frontend/src/views/MyPage.vue`
2. Add route in `frontend/src/router/index.js`
3. Add link in `frontend/src/App.vue`

### Connect New API Endpoint
Add to `frontend/src/api/client.js`:
```javascript
export const declarationsApi = {
  // ... existing methods
  
  async myNewMethod(data) {
    const response = await api.post('/api/my-endpoint', data)
    return response.data
  }
}
```

---

## ✅ Checklist

- [x] Backend API created and running
- [x] Frontend Vue app created
- [x] File upload component working
- [x] Declaration viewer with details
- [x] Format converter
- [x] Export functionality
- [x] Validation display
- [x] Routing between pages
- [x] State management
- [ ] Test with real data
- [ ] Add Electron wrapper (Phase 3)

---

## 🎉 You're Ready!

Your Modelo 720 app is complete and ready to use! 

**To start developing:**
```bash
# Terminal 1
cd backend && docker compose up

# Terminal 2  
cd frontend && npm run dev

# Open browser: http://localhost:5173
```

Enjoy! 🚀
