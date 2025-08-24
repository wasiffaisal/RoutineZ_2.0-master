# RoutineZ Development Setup Guide

This guide provides comprehensive instructions for setting up the RoutineZ development environment on your local machine.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux Ubuntu 18.04+
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 2GB free space for dependencies
- **Network**: Stable internet connection for API calls

### Required Software

#### 1. Python 3.8+
**Windows:**
```bash
# Download from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
python --version  # Should show 3.8+
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.8
python3 --version  # Should show 3.8+
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev

# CentOS/RHEL
sudo yum install python38 python38-devel
```

#### 2. Node.js 16+
**All Platforms:**
```bash
# Download from https://nodejs.org/
# LTS version recommended
node --version  # Should show 16+
npm --version   # Should show 8+
```

#### 3. Git
```bash
# Verify installation
git --version
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/cswasif/RoutineZ_2.0.git
cd RoutineZ_2.0
```

### 2. Environment Setup Script
For convenience, we've provided setup scripts:

**Windows (PowerShell):**
```powershell
# Run the setup script
.\scripts\setup-windows.ps1
```

**macOS/Linux:**
```bash
# Make script executable
chmod +x scripts/setup-unix.sh
./scripts/setup-unix.sh
```

## Detailed Setup

### Backend Setup (Flask API)

#### 1. Navigate to API Directory
```bash
cd api
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration
Create `.env` file in the `api/` directory:

```bash
# Required for AI features
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional configurations
DEBUG=true
PORT=5000
FLASK_ENV=development

# Database (if using local storage)
DATABASE_URL=sqlite:///routinez.db

# API Keys for external services
CONNAPI_URL=https://connectlive-nine.vercel.app
CACHE_TTL=300
```

#### 5. Verify Installation
```bash
# Test Python imports
python -c "import flask, requests, google.generativeai; print('All imports successful')"

# Test data loading
python -c "from routinez.data_loader import load_data; print(f'Loaded {len(load_data())} courses')"
```

#### 6. Run Development Server
```bash
# Development mode with auto-reload
python -m routinez.main

# Or using Flask directly
flask run --host=0.0.0.0 --port=5000

# Production mode
python -m gunicorn routinez.main:app -b 0.0.0.0:5000
```

### Frontend Setup (React)

#### 1. Navigate to Frontend Directory
```bash
cd USIS/usis-frontend
```

#### 2. Install Dependencies
```bash
# Clean install (recommended)
npm ci

# Or regular install
npm install
```

#### 3. Environment Configuration
Create `.env` file in the frontend directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:5000
REACT_APP_API_VERSION=v2

# Development settings
REACT_APP_DEBUG=true
REACT_APP_MOCK_API=false

# Feature flags
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_ANALYTICS=false

# Build optimization
GENERATE_SOURCEMAP=true
```

#### 4. Verify Installation
```bash
# Check for TypeScript errors
npm run type-check

# Run linting
npm run lint

# Run tests
npm test --watchAll=false
```

#### 5. Start Development Server
```bash
# Standard development
npm start

# With custom port
PORT=3001 npm start

# With HTTPS (for testing PWA)
HTTPS=true npm start
```

## Development Tools

### VS Code Setup

#### 1. Install Extensions
Create `.vscode/extensions.json`:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag"
  ]
}
```

#### 2. Workspace Settings
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./api/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Database Setup (Optional)

#### SQLite (Development)
```bash
# Create database
python -c "
from routinez.database import init_db
init_db()
print('Database initialized')
"
```

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
# Create database
createdb routinez_dev

# Set connection string
export DATABASE_URL=postgresql://user:password@localhost/routinez_dev
```

## Testing

### Backend Testing

#### 1. Install Testing Dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

#### 2. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=routinez --cov-report=html

# Run specific test file
pytest test_routinez.py -v

# Run with debug
pytest -s --pdb
```

#### 3. Test Structure
```
api/
├── tests/
│   ├── test_routes.py
│   ├── test_ai_service.py
│   ├── test_data_loader.py
│   └── conftest.py
```

### Frontend Testing

#### 1. Testing Commands
```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

#### 2. Test Structure
```
USIS/usis-frontend/
├── src/
│   ├── __tests__/
│   ├── components/__tests__/
│   └── utils/__tests__/
```

## Debugging

### Backend Debugging

#### 1. Enable Debug Mode
```bash
export DEBUG=true
export FLASK_DEBUG=1
```

#### 2. Logging Configuration
```python
# Add to your .env
LOG_LEVEL=DEBUG
LOG_FILE=app.log
```

#### 3. Common Issues

**Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Fix relative imports
export PYTHONPATH=$PWD/api
```

**Port Already in Use:**
```bash
# Find process using port
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Frontend Debugging

#### 1. React Developer Tools
Install browser extension and enable in development.

#### 2. Network Debugging
```bash
# Enable detailed logging
REACT_APP_DEBUG_NETWORK=true npm start
```

#### 3. Build Issues
```bash
# Clear cache and reinstall
npm run clean
npm install

# Check for dependency issues
npm audit fix
```

## Environment-Specific Configurations

### Development Environment

#### Backend (`.env.development`)
```bash
DEBUG=true
FLASK_ENV=development
GOOGLE_API_KEY=dev_key
CONNAPI_MOCK=true
CACHE_TTL=60
```

#### Frontend (`.env.development`)
```bash
REACT_APP_API_URL=http://localhost:5000
REACT_APP_DEBUG=true
REACT_APP_MOCK_API=true
```

### Production Environment

#### Backend (`.env.production`)
```bash
DEBUG=false
FLASK_ENV=production
GOOGLE_API_KEY=production_key
CACHE_TTL=300
GUNICORN_WORKERS=4
```

#### Frontend (`.env.production`)
```bash
REACT_APP_API_URL=https://routinez-api.vercel.app
REACT_APP_DEBUG=false
GENERATE_SOURCEMAP=false
```

## Performance Optimization

### Backend Optimization

#### 1. Caching Setup
```python
# Redis caching (optional)
pip install redis
```

#### 2. Database Optimization
```python
# Connection pooling
pip install sqlalchemy
```

### Frontend Optimization

#### 1. Bundle Analysis
```bash
npm run build
npm run analyze
```

#### 2. Code Splitting
```javascript
// Lazy load components
const LazyComponent = React.lazy(() => import('./LazyComponent'));
```

## Security Setup

### Backend Security

#### 1. Environment Variables
```bash
# Never commit secrets
# Use .env files for development
# Use Vercel/Netlify environment variables for production
```

#### 2. CORS Configuration
```python
# Restrict origins in production
CORS(app, origins=['https://routinez.vercel.app'])
```

### Frontend Security

#### 1. Content Security Policy
```html
<!-- Add to public/index.html -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">
```

## Monitoring

### Backend Monitoring

#### 1. Health Checks
```bash
# Create health check endpoint
curl http://localhost:5000/api/health
```

#### 2. Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Frontend Monitoring

#### 1. Performance Monitoring
```javascript
// Add to App.js
import { reportWebVitals } from './reportWebVitals';
reportWebVitals(console.log);
```

## Troubleshooting

### Common Setup Issues

#### 1. Python Path Issues
```bash
# Windows
set PYTHONPATH=%CD%\api

# macOS/Linux
export PYTHONPATH=$PWD/api
```

#### 2. Node Version Issues
```bash
# Use Node Version Manager
# Windows: nvm-windows
# macOS/Linux: nvm
nvm use 16
```

#### 3. Permission Issues (macOS/Linux)
```bash
# Fix permission errors
sudo chown -R $USER:$USER .
```

#### 4. Firewall Issues
```bash
# Allow ports through firewall
# Windows: Windows Defender Firewall
# macOS: System Preferences > Security & Privacy
# Linux: ufw allow 5000
```

## Getting Help

### Documentation
- [API Documentation](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

### Community
- **GitHub Issues**: [Report bugs here](https://github.com/cswasif/RoutineZ_2.0/issues)
- **Discord**: [Join our community](https://discord.gg/routinez)
- **Email**: wasif.faisal@bracu.ac.bd

### Support Resources
- **FAQ**: Check the troubleshooting section above
- **Video Tutorials**: Coming soon
- **Live Support**: Available during BRACU office hours