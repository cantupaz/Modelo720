# Modelo 720 App - Project Roadmap

## 📋 Project Overview

Building a desktop and web application for Spanish Modelo 720 tax declarations using:
- **Backend**: FastAPI (Python)
- **Frontend**: Vue 3 + Vite
- **Desktop**: Electron wrapper
- **Core Library**: Existing Modelo720 Python library

---

## ✅ Phase 1: Backend API (COMPLETED)

### Created Structure
```
backend/
├── app/
│   ├── main.py                     # FastAPI app with CORS
│   ├── api/                        # Route handlers
│   │   ├── health.py              # Health checks
│   │   └── declarations.py        # Main CRUD operations
│   ├── services/                   # Business logic
│   │   └── declaration_service.py # Wraps Modelo720 library
│   └── models/                     # API data models
│       └── declaration_models.py  # Pydantic models
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py
```

### API Endpoints
- ✅ `GET /health` - Health check
- ✅ `POST /api/declarations/parse` - Parse .720 or CSV files
- ✅ `POST /api/declarations/validate` - Validate declarations
- ✅ `POST /api/declarations/convert` - Convert between formats
- ✅ `POST /api/declarations/export` - Export to file

### What Works
- File upload handling with multipart/form-data
- Conversion between fixed-width .720 and CSV formats
- Full validation using existing library
- File download responses
- Auto-generated API documentation (Swagger/ReDoc)

---

## 🔄 Phase 2: Vue3 Frontend (NEXT)

### Recommended Stack
- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **State Management**: Pinia
- **HTTP Client**: Axios
- **UI Framework**: 
  - Option A: Vuetify 3 (Material Design)
  - Option B: Element Plus
  - Option C: PrimeVue
  - Option D: Tailwind CSS + HeadlessUI
- **Form Handling**: VeeValidate + Yup
- **File Upload**: vue-dropzone or custom component

### Planned Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUploader.vue       # Drag-drop file upload
│   │   ├── DeclarationViewer.vue  # Display parsed data
│   │   ├── DeclarationEditor.vue  # Edit declaration fields
│   │   ├── ValidationResults.vue  # Show validation errors
│   │   └── FormatConverter.vue    # Convert between formats
│   ├── views/
│   │   ├── Home.vue               # Landing page
│   │   ├── Parse.vue              # Upload and parse
│   │   ├── Edit.vue               # Edit declaration
│   │   └── Convert.vue            # Format conversion tool
│   ├── stores/
│   │   └── declarationStore.js    # Pinia store for state
│   ├── api/
│   │   └── client.js              # Axios API client
│   ├── router/
│   │   └── index.js               # Vue Router config
│   ├── App.vue
│   └── main.js
├── package.json
├── vite.config.js
└── index.html
```

### Key Features to Implement

1. **File Upload Component**
   - Drag-and-drop interface
   - File type validation (.720, .csv)
   - Upload progress indicator
   - Parse on upload

2. **Declaration Viewer**
   - Display header information
   - Table of detail records (bienes)
   - Expandable detail rows
   - Search/filter capabilities

3. **Declaration Editor**
   - Form for header fields
   - Add/edit/delete detail records
   - Field validation (NIF, dates, amounts)
   - Auto-save to store

4. **Validation Panel**
   - Real-time validation
   - Error highlighting
   - Warning messages
   - Fix suggestions

5. **Format Converter**
   - Upload one format, download another
   - Side-by-side comparison
   - Batch conversion

6. **Export Module**
   - Generate .720 files
   - Generate CSV files
   - Download with proper filename

### Development Steps

1. **Setup** (1-2 days)
   ```bash
   npm create vite@latest frontend -- --template vue
   cd frontend
   npm install pinia vue-router axios
   ```

2. **Core Layout** (1 day)
   - Navigation bar
   - Sidebar menu
   - Main content area
   - Footer

3. **API Integration** (1 day)
   - Create Axios instance with base URL
   - API client functions
   - Error handling
   - Request/response interceptors

4. **File Upload** (1-2 days)
   - Upload component
   - Integration with parse endpoint
   - Response handling

5. **Data Display** (2-3 days)
   - Header display component
   - Details table component
   - JSON viewer (fallback)

6. **Editing Features** (3-4 days)
   - Form components
   - Validation
   - State management

7. **Polish** (2-3 days)
   - Loading states
   - Error handling
   - Responsive design
   - Accessibility

---

## 🖥️ Phase 3: Electron Integration

### Architecture Choices

**Option A: Embedded Backend (Recommended for Desktop)**
```
Electron Main Process
├── Spawn FastAPI server (localhost:8000)
├── Wait for server ready
└── Create window → http://localhost:8000
```

**Option B: Separate Processes**
```
User manually starts backend
Electron connects to existing server
```

### Implementation Plan

1. **Add Electron to Frontend** (1 day)
   ```bash
   cd frontend
   npm install --save-dev electron electron-builder
   ```

2. **Create Electron Main Process** (1 day)
   ```javascript
   // electron/main.js
   - Spawn FastAPI Python process
   - Create BrowserWindow
   - Handle IPC for file system access
   - Package Python with PyInstaller
   ```

3. **Build Configuration** (1 day)
   - electron-builder config
   - Package Python backend
   - Create installers (Windows, macOS, Linux)

4. **Testing** (1-2 days)
   - Test on all platforms
   - Handle subprocess lifecycle
   - Error handling for backend failures

### File Structure
```
frontend/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Context bridge
│   └── start-backend.js     # Spawn FastAPI
├── dist-electron/           # Built desktop app
└── package.json             # Scripts for electron
```

---

## 📦 Phase 4: Packaging & Distribution

### Desktop App (Electron)
- **Windows**: .exe installer (NSIS)
- **macOS**: .dmg, .app bundle
- **Linux**: .AppImage, .deb, .rpm

### Web App
- **Frontend**: Static hosting (Vercel, Netlify, Cloudflare Pages)
- **Backend**: 
  - VPS (DigitalOcean, Linode)
  - Docker deployment
  - Serverless? (AWS Lambda + API Gateway)

---

## 🎯 Recommended Next Steps

### Immediate (Today/Tomorrow)

1. **Test Backend API**
   ```bash
   cd backend
   # Install deps (see SETUP.md)
   python3 run.py
   # Test with curl or browser
   ```

2. **Initialize Vue Frontend**
   ```bash
   npm create vite@latest frontend -- --template vue
   cd frontend
   npm install
   npm run dev
   ```

3. **Create First Component**
   - Simple file upload form
   - Call backend parse endpoint
   - Display response JSON

### Short Term (This Week)

1. Build core UI components
2. Implement state management
3. Connect all API endpoints
4. Basic styling

### Medium Term (Next 2 Weeks)

1. Complete feature set
2. Add Electron wrapper
3. Test desktop build
4. Polish UI/UX

---

## 🛠️ Technology Decisions to Make

### UI Framework
**Recommendation**: Start with Tailwind CSS + HeadlessUI
- Most flexible
- Smallest bundle size
- Easy to customize
- Modern look

### Form Library
**Recommendation**: VeeValidate
- Vue 3 native
- Great TypeScript support
- Flexible validation rules

### File Upload
**Recommendation**: Custom component with `<input type="file">`
- Full control
- No extra dependencies
- Easy to style

---

## 📊 Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Backend API | 1 day | ✅ DONE |
| Phase 2: Vue Frontend | 1-2 weeks | 🔄 NEXT |
| Phase 3: Electron | 3-5 days | ⏳ PENDING |
| Phase 4: Polish & Deploy | 3-5 days | ⏳ PENDING |

**Total**: 3-4 weeks for MVP

---

## 🚀 Getting Started Now

Run these commands to start development:

```bash
# Terminal 1: Start Backend
cd /home/erick/Modelo720/backend
python3 run.py

# Terminal 2: Create and Start Frontend (next step)
cd /home/erick/Modelo720
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm run dev
```

Then open:
- Backend API docs: http://localhost:8000/docs
- Frontend app: http://localhost:5173

---

## 📚 Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Vue 3**: https://vuejs.org/
- **Vite**: https://vitejs.dev/
- **Pinia**: https://pinia.vuejs.org/
- **Electron**: https://www.electronjs.org/
- **Electron Builder**: https://www.electron.build/

---

**Questions? Concerns? Ready to proceed with Vue3 frontend?**
