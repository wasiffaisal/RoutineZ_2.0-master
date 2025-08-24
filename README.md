# RoutineZ 2.0 - AI-Powered Course Scheduling for BRAC University

<p align="center">
   <img src="assets/logo.png" alt="RoutineZ Logo" width="300" height="300"/>
</p>

<div align="center">
  <h3>🎓 Next-Generation Smart Course Scheduling for BRACU Students</h3>
  <p><strong>Live Demo:</strong> <a href="https://routinez.vercel.app">https://routinez.vercel.app</a></p>
  <p>Built exclusively for BRAC University students with live BracU Connect integration and AI-powered optimization</p>
  
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
  [![React](https://img.shields.io/badge/React-18%2B-blue)](https://reactjs.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.0%2B-blue)](https://flask.palletsprojects.com/)
  [![Vercel](https://img.shields.io/badge/Vercel-Deployed-green)](https://vercel.com)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

## 🌟 What's New in RoutineZ 2.0

### 🔥 Enhanced AI Capabilities
- **Advanced Gemini AI Integration**: Smarter schedule optimization with contextual understanding
- **Multi-factor Optimization**: Considers commute time, faculty ratings, and personal preferences
- **Predictive Scheduling**: AI learns from your preferences to suggest better schedules
- **Natural Language Interface**: Ask questions about your schedule in plain English

### 🚀 Performance Improvements
- **50% Faster Generation**: Optimized algorithms for instant schedule creation
- **Real-time Data Streaming**: Live updates without page refresh
- **Enhanced Caching**: Smart data management for faster load times
- **Progressive Web App**: Install as a native app on your device

### 🎯 New Features
- **Mobile-First Design**: Completely redesigned for mobile users
- **Dark Mode Support**: Eye-friendly interface for late-night planning
- **Schedule Sharing**: Share your routine with friends via link
- **Export Options**: Download as PDF, image, or calendar file
- **Offline Mode**: Access cached schedules without internet

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development Setup](#-development-setup)
- [Deployment Guide](#-deployment-guide)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### For Students (End Users)

1. **Visit the Live App**
   ```
   https://routinez.vercel.app
   ```

2. **Select Your Courses**
   - Browse available courses for the semester
   - Check real-time seat availability
   - View faculty information and ratings

3. **Set Your Preferences**
   - Choose preferred days and time slots
   - Set commute preferences (Live Far/Near)
   - Select preferred faculty members

4. **Generate Your Schedule**
   - Click "Generate Routine" for instant results
   - Use AI optimization for the best schedule
   - Review and adjust as needed

### For Developers

#### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

#### Clone the Repository
```bash
git clone https://github.com/cswasif/RoutineZ_2.0.git
cd RoutineZ_2.0
```

## 🏗️ Project Structure

```
RoutineZ_2.0/
├── api/                          # Flask Backend API
│   ├── routinez/
│   │   ├── __init__.py
│   │   ├── main.py              # Flask app factory
│   │   ├── routes.py            # API endpoints
│   │   ├── ai_service.py        # Gemini AI integration
│   │   ├── data_loader.py       # Data loading and caching
│   │   ├── exam_utils.py        # Exam conflict detection
│   │   ├── time_utils.py        # Time-related utilities
│   │   ├── utils.py             # General utilities
│   │   └── config.py            # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   └── test_routinez.py         # API tests
├── USIS/usis-frontend/          # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API service layer
│   │   ├── utils/               # Frontend utilities
│   │   └── styles/              # CSS and styling
│   ├── package.json             # Node.js dependencies
│   └── tsconfig.json           # TypeScript configuration
├── assets/                      # Static assets
├── docs/                        # Additional documentation
├── .gitignore
├── vercel.json                  # Vercel deployment config
├── requirements.txt             # Root Python dependencies
└── README.md
```

## 📡 API Documentation

### Base URL
```
https://routinez-api.vercel.app
```

### Authentication
All endpoints are public and don't require authentication.

### Rate Limits
- 100 requests per minute per IP
- 1000 requests per hour per IP

### Endpoints

#### 1. Health Check
```http
GET /api/connapi-status
```
**Response:**
```json
{
  "status": "online",
  "ai_available": true,
  "ai_message": "AI service is operational",
  "debug_mode": false
}
```

#### 2. Get All Courses
```http
GET /api/courses
```
**Response:**
```json
{
  "data": [
    {
      "course_code": "CSE110",
      "course_name": "Structured Programming Language",
      "sections": [
        {
          "section": "1",
          "faculty": "Dr. John Doe",
          "schedule": {
            "day": "MW",
            "time": "08:00-09:30",
            "room": "AC2-301"
          },
          "available_seats": 45,
          "total_seats": 50
        }
      ],
      "mid_exam": "2024-03-15T09:00:00Z",
      "final_exam": "2024-04-20T14:00:00Z"
    }
  ]
}
```

#### 3. Check Schedule Conflicts
```http
POST /api/check-conflicts
```
**Request:**
```json
{
  "selected_sections": [
    {
      "course_code": "CSE110",
      "section": "1"
    },
    {
      "course_code": "MAT110",
      "section": "2"
    }
  ]
}
```
**Response:**
```json
{
  "conflicts": [
    {
      "type": "time",
      "courses": ["CSE110", "MAT110"],
      "details": "Classes overlap on Monday 08:00-09:30"
    }
  ],
  "has_conflicts": true
}
```

#### 4. AI Schedule Optimization
```http
POST /api/ai-suggest
```
**Request:**
```json
{
  "prompt": "Generate an optimal schedule for 5 courses with no classes before 9 AM",
  "temperature": 0.7
}
```
**Response:**
```json
{
  "suggestion": "Based on your preferences, here's an optimized schedule...",
  "courses": ["CSE110", "MAT110", "PHY110"],
  "confidence": 0.92
}
```

### Error Handling
All endpoints return consistent error responses:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

## 🔧 Development Setup

### Backend Setup (Flask API)

#### 1. Create Virtual Environment
```bash
cd api
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Environment Variables
Create a `.env` file in the `api/` directory:
```bash
# Required for AI features
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Debug mode
DEBUG=true

# Optional: Custom port
PORT=5000
```

#### 4. Run Development Server
```bash
# Development mode
python -m routinez.main

# Production mode with gunicorn
gunicorn routinez.main:app
```

The API will be available at `http://localhost:5000`

### Frontend Setup (React)

#### 1. Navigate to Frontend Directory
```bash
cd USIS/usis-frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure API URL
Create a `.env` file in the frontend directory:
```bash
REACT_APP_API_URL=http://localhost:5000
```

#### 4. Start Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🚀 Deployment Guide

### Deploy to Vercel (Recommended)

#### Backend Deployment
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy RoutineZ 2.0"
   git push origin master
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set build settings:
     - **Framework**: Flask
     - **Root Directory**: `api`
     - **Build Command**: `pip install -r requirements.txt`
     - **Output Directory**: `.`

3. **Environment Variables**
   Add these in Vercel dashboard:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   PORT=5000
   ```

#### Frontend Deployment
1. **Build Production Version**
   ```bash
   cd USIS/usis-frontend
   npm run build
   ```

2. **Deploy to Vercel**
   - Create a new project on Vercel
   - Import the `USIS/usis-frontend` directory
   - Vercel will auto-detect React settings

### Alternative Deployment Options

#### Docker Deployment
Create a `Dockerfile` in the root directory:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install -r requirements.txt

COPY api/ .

EXPOSE 5000

CMD ["gunicorn", "routinez.main:app", "-b", "0.0.0.0:5000"]
```

Build and run:
```bash
docker build -t routinez-api .
docker run -p 5000:5000 -e GOOGLE_API_KEY=your_key routinez-api
```

#### Heroku Deployment
1. Create `Procfile`:
   ```
   web: gunicorn routinez.main:app
   ```

2. Deploy:
   ```bash
   heroku create routinez-api
   git push heroku master
   ```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add: AI-powered schedule optimization"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Create a Pull Request**

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Write unit tests for new features
- Add docstrings for all functions

#### JavaScript/React (Frontend)
- Use TypeScript for new components
- Follow React best practices
- Write component tests with Jest
- Use meaningful component names

#### Git Commit Messages
```
Add: New feature or enhancement
Fix: Bug fix
Update: Update existing feature
Docs: Documentation changes
Test: Add or update tests
Refactor: Code refactoring
Style: Code style changes
```

### Testing

#### Backend Tests
```bash
cd api
python test_routinez.py
```

#### Frontend Tests
```bash
cd USIS/usis-frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Connection Issues
**Problem**: Frontend can't connect to backend
**Solution**:
```bash
# Check if backend is running
curl http://localhost:5000/api/test

# Check CORS settings in routes.py
```

#### 2. AI Service Not Working
**Problem**: AI suggestions not generating
**Solution**:
```bash
# Check API key
export GOOGLE_API_KEY=your_key_here

# Verify AI service initialization
python -c "from routinez.ai_service import check_ai_availability; print(check_ai_availability())"
```

#### 3. Data Loading Issues
**Problem**: No course data available
**Solution**:
```bash
# Check data source connectivity
python -c "from routinez.data_loader import load_data; print(len(load_data()))"

# Check network connectivity to BracU Connect
```

#### 4. Frontend Build Issues
**Problem**: npm build fails
**Solution**:
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run build
```

### Performance Optimization

#### Backend
- Use Redis for caching (optional)
- Implement rate limiting
- Optimize database queries
- Use CDN for static assets

#### Frontend
- Implement lazy loading
- Use React.memo for components
- Optimize bundle size
- Enable service worker

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **Health Check**: `/api/connapi-status`
- **Performance Metrics**: Response times logged
- **Error Tracking**: Comprehensive error logging

### Adding Analytics
```javascript
// Example: Add Google Analytics
import ReactGA from 'react-ga';
ReactGA.initialize('GA_TRACKING_ID');
```

## 🔐 Security

### Best Practices
- Input validation on all endpoints
- Rate limiting to prevent abuse
- HTTPS enforcement in production
- No sensitive data in logs
- Environment variables for secrets

### Security Headers
```python
# Add to Flask app
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

## 📞 Support

### Getting Help
- **GitHub Issues**: [Report bugs here](https://github.com/cswasif/RoutineZ_2.0/issues)
- **Email**: wasif.faisal@bracu.ac.bd
- **Discord**: [Join our community](https://discord.gg/routinez)

### API Status
Check the current API status at:
```
https://routinez-api.vercel.app/api/connapi-status
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BRAC University** - For providing the course data
- **ConnAPI Team** - For the amazing API integration
- **Google AI** - For Gemini AI integration
- **Contributors** - All the amazing people who contributed

---

<div align="center">
  <p><strong>Made with ❤️ for BRACU students by <a href="https://github.com/cswasif">Wasif Faisal</a></strong></p>
  <p>
    <a href="https://routinez.vercel.app">🚀 Try RoutineZ Now</a> |
    <a href="https://github.com/cswasif/RoutineZ_2.0">⭐ Star on GitHub</a> |
    <a href="https://github.com/cswasif/RoutineZ_2.0/issues">🐛 Report Issues</a>
  </p>
</div>