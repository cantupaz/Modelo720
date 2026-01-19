# 🐳 Dev Container Quick Reference

## TL;DR - Just Start Coding!

```bash
# Option 1: Everything in one command
./quick-start.sh

# Option 2: Docker Compose (Recommended)
docker compose -f docker-compose.dev.yml up

# Option 3: VS Code Dev Container
# Open in VS Code → F1 → "Dev Containers: Reopen in Container"
# Then run: ./start-dev.sh
```

---

## 🎯 Three Ways to Develop

### 1️⃣ **Docker Compose** (Easiest)
No Node.js or Python needed on your machine!

```bash
docker compose -f docker-compose.dev.yml up
```

- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ Hot reload for both
- ✅ All dependencies in containers

**To stop:** `Ctrl+C` or `docker compose -f docker-compose.dev.yml down`

---

### 2️⃣ **VS Code Dev Container** (Best for Coding)
Full IDE experience inside container!

**Setup:**
1. Install [VS Code](https://code.visualstudio.com/) 
2. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. Open project: `code /home/erick/Modelo720`
4. Press `F1` → Type "Dev Containers: Reopen in Container"
5. Wait for build (first time only)

**Inside container:**
```bash
./start-dev.sh
```

**Benefits:**
- Full IntelliSense and debugging
- All extensions work
- Terminal runs inside container
- No host machine pollution

---

### 3️⃣ **Backend + Frontend Separately**
Run services in separate containers:

```bash
# Start both
cd backend && docker compose up

# In another terminal for logs
docker compose -f backend/docker-compose.yml logs -f frontend
```

---

## 📋 What's Available

### Services in docker-compose.dev.yml:

1. **`dev`** - Full dev environment (Python + Node.js)
   - For VS Code dev container
   - Shell access to run commands manually

2. **`backend`** - Backend API only
   - FastAPI on port 8000
   - Auto-reload on code changes

3. **`frontend`** - Frontend only
   - Vue/Vite on port 5173
   - Auto-reload on code changes

---

## 🚀 Common Tasks

### Start Everything
```bash
docker compose -f docker-compose.dev.yml up
```

### Start in Background
```bash
docker compose -f docker-compose.dev.yml up -d
```

### View Logs
```bash
docker compose -f docker-compose.dev.yml logs -f
```

### Stop Everything
```bash
docker compose -f docker-compose.dev.yml down
```

### Rebuild After Changes
```bash
docker compose -f docker-compose.dev.yml up --build
```

### Shell Access
```bash
# Into dev container
docker compose -f docker-compose.dev.yml exec dev bash

# Into backend
docker compose -f docker-compose.dev.yml exec backend bash

# Into frontend
docker compose -f docker-compose.dev.yml exec frontend sh
```

### Install Packages Inside Container
```bash
# Python package (backend)
docker compose -f docker-compose.dev.yml exec backend pip install <package>

# npm package (frontend)
docker compose -f docker-compose.dev.yml exec frontend npm install <package>
```

---

## 🛠️ File Structure

```
Modelo720/
├── .devcontainer/
│   └── devcontainer.json        # VS Code dev container config
├── Dockerfile.dev                # Dev container image (Python + Node.js)
├── docker-compose.dev.yml        # Development services
├── start-dev.sh                  # Helper script (use inside container)
├── quick-start.sh                # Quick start menu
├── backend/
│   ├── docker-compose.yml        # Backend + Frontend separate
│   └── Dockerfile                # Production backend
└── frontend/
    └── (Vue app files)
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Stop all containers
docker compose -f docker-compose.dev.yml down

# Or kill specific port
lsof -ti:8000 | xargs kill -9
```

### Changes Not Reflecting
Make sure volumes are mounted:
```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up --build
```

### Cannot Connect to Backend from Frontend
The frontend in container should use:
- `http://localhost:8000` (from host)
- `http://backend:8000` (from frontend container)

Vite proxy is configured in `frontend/vite.config.js`

### VS Code Dev Container Won't Start
```bash
# Rebuild
docker compose -f docker-compose.dev.yml build --no-cache dev

# Or use VS Code command:
# F1 → "Dev Containers: Rebuild Container"
```

---

## 🎨 Customization

### Add Python Package
Edit `backend/requirements.txt`, then:
```bash
docker compose -f docker-compose.dev.yml up --build backend
```

### Add npm Package
```bash
docker compose -f docker-compose.dev.yml exec frontend npm install <package>
# Commit the changes to package.json and package-lock.json
```

### Change Ports
Edit `docker-compose.dev.yml`:
```yaml
ports:
  - "8001:8000"  # Backend on 8001
  - "3000:5173"  # Frontend on 3000
```

---

## ✅ Verify Setup

After starting containers:

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend (in browser)
open http://localhost:5173

# Check API docs
open http://localhost:8000/docs
```

---

## 📚 More Info

- Full guide: [DEV_CONTAINER_GUIDE.md](DEV_CONTAINER_GUIDE.md)
- Getting started: [GETTING_STARTED.md](GETTING_STARTED.md)
- Project roadmap: [ROADMAP.md](ROADMAP.md)

---

**Need help?** Check the full [DEV_CONTAINER_GUIDE.md](DEV_CONTAINER_GUIDE.md) for detailed instructions!
