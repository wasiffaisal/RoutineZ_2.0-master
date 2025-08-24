# RoutineZ Deployment Guide

This guide covers deploying RoutineZ to various platforms including Vercel, Netlify, Heroku, and traditional servers.

## Platform Comparison

| Platform | Backend | Frontend | Database | Cost | Complexity |
|----------|---------|----------|----------|------|------------|
| Vercel | ✅ Serverless | ✅ Static | ❌ | Free tier | Easy |
| Netlify | ✅ Functions | ✅ Static | ❌ | Free tier | Easy |
| Heroku | ✅ Full stack | ✅ Static | ✅ Postgres | Free tier | Medium |
| DigitalOcean | ✅ Full stack | ✅ Static | ✅ Any | $5+/mo | Medium |
| AWS | ✅ All options | ✅ All options | ✅ All | Pay-as-you-go | Complex |

## Vercel Deployment (Recommended)

### Prerequisites
- Vercel account (free)
- GitHub repository connected

### Frontend Deployment

#### 1. Install Vercel CLI
```bash
npm i -g vercel
```

#### 2. Deploy Frontend
```bash
cd USIS/usis-frontend
vercel --prod
```

#### 3. Configure Environment Variables
In Vercel dashboard:
- `REACT_APP_API_URL`: Your backend URL
- `REACT_APP_API_VERSION`: v2
- `REACT_APP_ENABLE_AI`: true

### Backend Deployment (Serverless)

#### 1. Prepare Backend
```bash
cd api
pip install -r requirements.txt
```

#### 2. Create vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/usisvercel.py",
      "use": "@vercel/python"
    },
    {
      "src": "USIS/usis-frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/usisvercel.py"
    },
    {
      "src": "/(.*)",
      "dest": "/USIS/usis-frontend/build/$1"
    }
  ],
  "env": {
    "GOOGLE_API_KEY": "@google-api-key"
  }
}
```

**Note:** Make sure to remove any waitress dependencies from your requirements.txt as they are not needed for Vercel serverless functions and will cause deployment errors.

#### 3. Deploy
```bash
vercel --prod
```

## Netlify Deployment

### Frontend Deployment

#### 1. Build Frontend
```bash
cd USIS/usis-frontend
npm run build
```

#### 2. Deploy via CLI
```bash
netlify deploy --prod --dir=build
```

#### 3. Configure Environment Variables
In Netlify dashboard:
- Build command: `npm run build`
- Publish directory: `build`
- Environment variables: Same as Vercel

### Backend Functions

#### 1. Create Netlify Functions
```bash
# Create functions directory
mkdir netlify/functions

# Create API function
cp api/routinez/main.py netlify/functions/api.py
```

#### 2. Configure netlify.toml
```toml
[build]
  functions = "netlify/functions"
  publish = "USIS/usis-frontend/build"

[build.environment]
  PYTHON_VERSION = "3.8"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
```

## Heroku Deployment

### Full Stack Deployment

#### 1. Install Heroku CLI
```bash
# Windows
choco install heroku-cli

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Prepare Backend
Create `Procfile` in root:
```
web: gunicorn api.routinez.main:app --bind 0.0.0.0:$PORT
```

#### 3. Create runtime.txt
```
python-3.8.10
```

#### 4. Deploy
```bash
# Initialize Heroku
git init
heroku create routinez-app

# Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_key_here
heroku config:set DEBUG=false

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku master
```

### Database Setup (Heroku Postgres)

#### 1. Add Database
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

#### 2. Configure Database
```python
# Update config.py
import os
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
```

## DigitalOcean Deployment

### Droplet Setup

#### 1. Create Droplet
- Ubuntu 20.04 LTS
- 1GB RAM minimum
- 25GB SSD

#### 2. Initial Setup
```bash
# Connect to droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3-pip python3-venv nginx -y
```

#### 3. Deploy Backend
```bash
# Clone repository
git clone https://github.com/cswasif/RoutineZ_2.0.git
cd RoutineZ_2.0/api

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/routinez.service
```

#### 4. Create Service File
```ini
[Unit]
Description=RoutineZ API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/routinez/RoutineZ_2.0/api
Environment="PATH=/home/routinez/RoutineZ_2.0/api/venv/bin"
ExecStart=/home/routinez/RoutineZ_2.0/api/venv/bin/gunicorn --workers 3 --bind unix:/home/routinez/RoutineZ_2.0/api/routinez.sock routinez.main:app

[Install]
WantedBy=multi-user.target
```

#### 5. Configure Nginx
```nginx
# /etc/nginx/sites-available/routinez
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://unix:/home/routinez/RoutineZ_2.0/api/routinez.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/routinez/RoutineZ_2.0/USIS/usis-frontend/build/static;
    }
}
```

### Frontend Deployment

#### 1. Build Frontend
```bash
cd USIS/usis-frontend
npm ci
npm run build
```

#### 2. Serve Static Files
```bash
# Copy build to web root
sudo cp -r build/* /var/www/html/
```

## AWS Deployment

### EC2 Setup

#### 1. Launch Instance
- Amazon Linux 2
- t2.micro (free tier)
- Security group: HTTP (80), HTTPS (443), SSH (22)

#### 2. Install Dependencies
```bash
# Update system
sudo yum update -y
sudo yum install python3 python3-pip nginx -y

# Install Node.js
curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install nodejs -y
```

#### 3. Deploy with Docker (Recommended)

#### 1. Create Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY api/ .
CMD ["gunicorn", "routinez.main:app", "--bind", "0.0.0.0:5000"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./api:/app

  frontend:
    build: ./USIS/usis-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

## Environment Variables

### Production Variables

#### Backend (.env.production)
```bash
# Required
GOOGLE_API_KEY=your_production_key
FLASK_ENV=production
DEBUG=false

# Optional
PORT=5000
DATABASE_URL=postgresql://...
CACHE_TTL=300
RATE_LIMIT=100
```

#### Frontend (.env.production)
```bash
# Required
REACT_APP_API_URL=https://api.routinez.app
REACT_APP_API_VERSION=v2

# Optional
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_SENTRY_DSN=your_sentry_dsn
```

## SSL/HTTPS Setup

### Let's Encrypt (Free SSL)

#### 1. Install Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# Amazon Linux
sudo yum install certbot python3-certbot-nginx
```

#### 2. Generate Certificate
```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

#### 3. Auto-renewal
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Analytics

### Application Monitoring

#### 1. Sentry Integration
```bash
# Backend
pip install sentry-sdk[flask]

# Frontend
npm install @sentry/react @sentry/tracing
```

#### 2. Google Analytics
```javascript
// Frontend tracking
import ReactGA from 'react-ga';
ReactGA.initialize('GA_TRACKING_ID');
```

### Performance Monitoring

#### 1. New Relic
```bash
# Backend
pip install newrelic
newrelic-admin generate-config YOUR_LICENSE_KEY newrelic.ini
```

#### 2. Datadog
```bash
# Backend
pip install datadog
```

## Backup & Recovery

### Database Backups

#### 1. Automated Backups
```bash
# Create backup script
#!/bin/bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. S3 Storage
```bash
# Upload to S3
aws s3 cp backup.sql s3://routinez-backups/
```

### Application Backups

#### 1. Git-based Backups
```bash
# Tag releases
git tag -a v2.0.0 -m "Production release"
git push origin v2.0.0
```

## Scaling

### Horizontal Scaling

#### 1. Load Balancer Setup
```nginx
upstream routinez_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}
```

#### 2. CDN Configuration
- Use Cloudflare for static assets
- Configure cache headers
- Enable compression

### Vertical Scaling

#### 1. Increase Resources
- Upgrade server specs
- Add more workers
- Increase memory limits

## Security Checklist

### Before Deployment
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error handling reviewed
- [ ] Dependencies updated
- [ ] Secrets removed from code

### Post-Deployment
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Monitoring alerts configured
- [ ] Backup schedule active
- [ ] Performance metrics baseline

## Troubleshooting

### Common Deployment Issues

#### 1. Build Failures
```bash
# Clear cache and retry
vercel --prod --force
```

#### 2. Environment Issues
```bash
# Check environment variables
heroku config
vercel env ls
```

#### 3. Database Connection
```bash
# Test connection
heroku pg:psql
```

### Support Resources
- **Deployment Issues**: [GitHub Issues](https://github.com/cswasif/RoutineZ_2.0/issues)
- **Platform Docs**: [Vercel](https://vercel.com/docs), [Heroku](https://devcenter.heroku.com/)
- **Community**: [Discord](https://discord.gg/routinez)