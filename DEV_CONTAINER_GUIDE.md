# Modelo 720 - Dev Container Setup

## 🐳 Development Container Options

You have **3 ways** to run the development environment without installing anything on your host machine:

---

## Option 1: Full Dev Container (Recommended for VS Code)

Best for: VS Code users who want a complete integrated development environment.

### Setup:
1. Install [VS Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project in VS Code
3. Press `F1` → "Dev Containers: Reopen in Container"
4. Wait for container to build (first time only)

### Once inside the container:
```bash
# Start both services
./start-dev.sh

# Or start individually:
# Terminal 1 - Backend
cd backend && python run.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

### Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 2: Docker Compose (Separate Services)

Best for: Running backend and frontend in separate containers with hot reload.

### Start everything:
```bash
docker compose -f docker-compose.dev.yml up
```

This will:
- Build both containers
- Start backend on port 8000
- Start frontend on port 5173
- Enable hot reload for both

### Individual services:
```bash
# Backend only
docker compose -f docker-compose.dev.yml up backend

# Frontend only
docker compose -f docker-compose.dev.yml up frontend

# Dev container (for shell access)
docker compose -f docker-compose.dev.yml up dev
```

### Stop:
```bash
docker compose -f docker-compose.dev.yml down
```

---

## Option 3: Production-like Setup (Current)

Best for: Testing the production build or when you don't need hot reload.

```bash
cd backend
docker compose up
```

This uses the original `backend/docker-compose.yml` which runs only the backend API.

---

## 📁 Files Created

```
Modelo720/
├── .devcontainer/
│   └── devcontainer.json          # VS Code dev container config
├── Dockerfile.dev                  # Dev container with Python + Node.js
├── docker-compose.dev.yml          # Development docker-compose
├── start-dev.sh                    # Helper script to start both services
├── backend/
│   └── docker-compose.yml          # Production-like backend setup
└── frontend/
    └── (your Vue app files)
```

---

## 🔧 Development Workflows

### Workflow 1: VS Code Dev Container (Full IDE)
```bash
# Open in VS Code
code .

# Reopen in container (F1 → Dev Containers: Reopen in Container)
# Inside container terminal:
./start-dev.sh
```

**Benefits:**
- ✅ Full IntelliSense and debugging
- ✅ Extensions work inside container
- ✅ No local dependencies needed
- ✅ Consistent environment

### Workflow 2: Docker Compose (Lightweight)
```bash
# Start services
docker compose -f docker-compose.dev.yml up

# In another terminal, exec into container if needed
docker compose -f docker-compose.dev.yml exec dev bash
```

**Benefits:**
- ✅ Lightweight
- ✅ Services restart automatically
- ✅ Easy to stop/start
- ✅ No VS Code required

### Workflow 3: Mixed (Backend in Docker, Frontend Local)
```bash
# Terminal 1: Backend in Docker
cd backend && docker compose up

# Terminal 2: Frontend locally (if you have Node.js)
cd frontend && npm run dev
```

---

## 🛠️ Commands Reference

### Dev Container Commands
```bash
# Rebuild dev container
docker compose -f docker-compose.dev.yml build dev

# Start with clean build
docker compose -f docker-compose.dev.yml up --build

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Shell access
docker compose -f docker-compose.dev.yml exec dev bash

# Stop everything
docker compose -f docker-compose.dev.yml down

# Remove volumes too
docker compose -f docker-compose.dev.yml down -v
```

### Inside Container
```bash
# Backend
cd /workspace/backend
python run.py

# Frontend
cd /workspace/frontend
npm run dev

# Both at once
/workspace/start-dev.sh

# Install Python package
pip install <package>

# Install npm package
cd /workspace/frontend && npm install <package>
```

---

## 🔍 Troubleshooting

### Port already in use
```bash
# Stop all containers
docker compose -f docker-compose.dev.yml down

# Or kill process on port
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Changes not reflecting
```bash
# For backend: restart container
docker compose -f docker-compose.dev.yml restart backend

# For frontend: should auto-reload (check Vite output)
```

### Container won't start
```bash
# View logs
docker compose -f docker-compose.dev.yml logs

# Rebuild from scratch
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up
```

### VS Code not detecting dev container
1. Make sure Docker is running
2. Install "Dev Containers" extension
3. Reload VS Code
4. Try: F1 → "Dev Containers: Rebuild Container"

---

## 📊 Comparison

| Feature | Dev Container | Docker Compose | Production Setup |
|---------|---------------|----------------|------------------|
| Hot Reload | ✅ | ✅ | ❌ |
| VS Code Integration | ✅ | ❌ | ❌ |
| Debugging | ✅ | ⚠️ | ❌ |
| Lightweight | ⚠️ | ✅ | ✅ |
| Easy Setup | ✅ | ✅ | ✅ |
| Both Services | ✅ | ✅ | Backend Only |

---

## 🎯 Recommended Setup

**For Development:**
```bash
docker compose -f docker-compose.dev.yml up
```

**For VS Code Users:**
1. Open project in VS Code
2. Install "Dev Containers" extension
3. Reopen in container
4. Run `./start-dev.sh`

**For Testing Backend API Only:**
```bash
cd backend && docker compose up
```

---

## ✅ Quick Start (Choose One)

### Option A: VS Code
```bash
code .
# Then: F1 → "Dev Containers: Reopen in Container"
# Inside container: ./start-dev.sh
```

### Option B: Docker Compose
```bash
docker compose -f docker-compose.dev.yml up
```

### Option C: Backend Only
```bash
cd backend && docker compose up
```

That's it! No Node.js or Python installation needed on your host machine! 🎉
