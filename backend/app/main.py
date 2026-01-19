"""
FastAPI backend for Modelo 720 application.
Provides REST API for parsing, validating, and converting Modelo 720 declarations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import declarations, health

app = FastAPI(
    title="Modelo 720 API",
    description="API for Spanish tax form 720 declarations",
    version="0.1.0"
)

# CORS configuration for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(declarations.router, prefix="/api/declarations", tags=["declarations"])


@app.get("/")
async def root():
    return {
        "message": "Modelo 720 API",
        "version": "0.1.0",
        "docs": "/docs"
    }
