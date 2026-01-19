#!/bin/bash
# Quick start for dev container - just run: ./quick-start.sh

echo "🚀 Modelo 720 - Dev Container Quick Start"
echo ""
echo "Choose an option:"
echo ""
echo "1) Full dev environment (VS Code recommended)"
echo "2) Docker Compose - Both services"
echo "3) Backend only"
echo "4) Backend + Frontend (separate containers)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    echo ""
    echo "📦 Starting full dev container..."
    echo "This includes Python + Node.js in one container"
    echo ""
    docker compose -f docker-compose.dev.yml up dev
    ;;
  2)
    echo ""
    echo "🐳 Starting both services with Docker Compose..."
    docker compose -f docker-compose.dev.yml up --build
    ;;
  3)
    echo ""
    echo "🔧 Starting backend only..."
    cd backend && docker compose up
    ;;
  4)
    echo ""
    echo "⚡ Starting backend and frontend in separate containers..."
    docker compose -f backend/docker-compose.yml up
    ;;
  *)
    echo "Invalid choice. Please run again and choose 1-4."
    exit 1
    ;;
esac
