# Modelo 720 API Backend

FastAPI backend for the Modelo 720 application.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the development server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Health
- `GET /health` - Health check

### Declarations
- `POST /api/declarations/parse` - Parse a .720 or .csv file
- `POST /api/declarations/validate` - Validate a declaration
- `POST /api/declarations/convert` - Convert between formats
- `POST /api/declarations/export` - Export a declaration to file

## Testing

Use curl or Postman to test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Parse a file
curl -X POST http://localhost:8000/api/declarations/parse \
  -F "file=@../example.720" \
  -F "format=720"

# Convert format
curl -X POST http://localhost:8000/api/declarations/convert \
  -F "file=@../example.720" \
  -F "source_format=720" \
  -F "target_format=csv" \
  --output converted.csv
```
