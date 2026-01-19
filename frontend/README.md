# Modelo 720 Frontend

Vue 3 + Vite frontend for the Modelo 720 application.

## Setup

1. Install Node.js and npm if not already installed:
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm
```

2. Install dependencies:
```bash
cd frontend
npm install
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Features

- **File Upload**: Drag-and-drop interface for .720 and CSV files
- **Declaration Viewer**: View parsed declaration data with all details
- **Validation**: Real-time validation with error reporting
- **Format Converter**: Convert between .720 and CSV formats
- **Export**: Download declarations in either format
- **History**: Keep track of recently viewed declarations

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable Vue components
│   │   ├── FileUploader.vue
│   │   ├── DeclarationViewer.vue
│   │   └── DetailView.vue
│   ├── views/           # Page components
│   │   ├── Home.vue
│   │   ├── Parse.vue
│   │   ├── Convert.vue
│   │   └── ViewDeclaration.vue
│   ├── stores/          # Pinia state management
│   │   └── declaration.js
│   ├── api/             # API client
│   │   └── client.js
│   ├── router/          # Vue Router
│   │   └── index.js
│   ├── App.vue
│   ├── main.js
│   └── style.css
├── package.json
├── vite.config.js
└── index.html
```

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Development

The frontend connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before starting the frontend.

### API Endpoints Used

- `POST /api/declarations/parse` - Parse uploaded files
- `POST /api/declarations/validate` - Validate declarations
- `POST /api/declarations/convert` - Convert between formats
- `POST /api/declarations/export` - Export declarations

## Technologies

- **Vue 3**: Progressive JavaScript framework
- **Vite**: Fast build tool and dev server
- **Vue Router**: Client-side routing
- **Pinia**: State management
- **Axios**: HTTP client
