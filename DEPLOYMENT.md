# Deployment Guide

## 🚀 Deploy Your E-Commerce Site

### Option 1: Local Development

**Already covered in QUICKSTART.md**

### Option 2: Deploy to Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git installed

#### Steps

1. **Create Procfile**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

2. **Add gunicorn to requirements**
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

3. **Initialize Git (if not already)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

5. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set MONGO_URI=your-mongodb-uri
   heroku config:set MONGO_DB_NAME=campus_cart
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Open your app**
   ```bash
   heroku open
   ```

### Option 3: Deploy to Railway

#### Steps

1. **Create railway.json**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "gunicorn app:app",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy on Railway**
   - Go to railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Add environment variables in Railway dashboard

### Option 4: Deploy to Render

#### Steps

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: campus-cart
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app:app
       envVars:
         - key: SECRET_KEY
           generateValue: true
         - key: MONGO_URI
           sync: false
         - key: MONGO_DB_NAME
           value: campus_cart
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render"
   git push origin main
   ```

3. **Deploy on Render**
   - Go to render.com
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect settings
   - Add environment variables
   - Click "Create Web Service"

### Option 5: Deploy to PythonAnywhere

#### Steps

1. **Upload files**
   - Zip your project
   - Upload to PythonAnywhere
   - Extract in your home directory

2. **Create virtual environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

3. **Configure WSGI**
   Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   path = '/home/yourusername/campus-cart'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

4. **Set environment variables**
   In WSGI file, add before imports:
   ```python
   import os
   os.environ['SECRET_KEY'] = 'your-secret-key'
   os.environ['MONGO_URI'] = 'your-mongodb-uri'
   os.environ['MONGO_DB_NAME'] = 'campus_cart'
   ```

5. **Reload web app**
   - Click "Reload" button in Web tab

## 🗄️ MongoDB Setup

### Option 1: MongoDB Atlas (Recommended for Production)

1. **Create account** at mongodb.com/cloud/atlas
2. **Create cluster** (Free tier available)
3. **Create database user**
4. **Whitelist IP** (0.0.0.0/0 for all IPs)
5. **Get connection string**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/campus_cart
   ```
6. **Set as MONGO_URI** in environment variables

### Option 2: Local MongoDB

1. **Install MongoDB** from mongodb.com
2. **Start MongoDB**
   ```bash
   mongod
   ```
3. **Use local URI**
   ```
   mongodb://localhost:27017/
   ```

### Option 3: MongoDB Docker

1. **Run MongoDB container**
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```
2. **Use Docker URI**
   ```
   mongodb://localhost:27017/
   ```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Set secure session cookies
- [ ] Configure CORS if needed
- [ ] Set up database backups
- [ ] Enable MongoDB authentication
- [ ] Whitelist only necessary IPs
- [ ] Review and test CSRF protection
- [ ] Set up error logging
- [ ] Configure rate limiting
- [ ] Review file upload security (if added)

## ⚙️ Production Configuration

### Update app.py for production

```python
if __name__ == "__main__":
    # Development
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Set Flask environment

```bash
export FLASK_ENV=production
```

### Disable debug mode

Ensure `debug=False` in production

### Configure logging

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

## 📊 Performance Optimization

### Enable Caching

Add Flask-Caching:
```bash
pip install Flask-Caching
```

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### Compress Responses

Add Flask-Compress:
```bash
pip install Flask-Compress
```

```python
from flask_compress import Compress
Compress(app)
```

### Database Indexing

Ensure indexes are created:
```python
# Already done in models.py init_indexes()
```

### Static File CDN

Consider using a CDN for static files:
- Cloudflare
- AWS CloudFront
- Google Cloud CDN

## 🔍 Monitoring

### Error Tracking

**Sentry Integration:**
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

### Application Monitoring

Consider:
- New Relic
- Datadog
- Application Insights

### Uptime Monitoring

Use:
- UptimeRobot
- Pingdom
- StatusCake

## 🧪 Pre-Deployment Testing

```bash
# Run tests
pytest test_app.py

# Check for security issues
pip install bandit
bandit -r .

# Check code quality
pip install flake8
flake8 app.py models.py config.py

# Test production build
gunicorn app:app
```

## 📝 Environment Variables

Required for production:

```env
# Required
SECRET_KEY=your-super-secret-key-min-32-chars
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB_NAME=campus_cart

# Optional
USE_MOCK_DB=false
LOG_LEVEL=INFO
FLASK_ENV=production
```

## 🔄 Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

## 📱 Domain Setup

### Custom Domain

1. **Purchase domain** (Namecheap, GoDaddy, etc.)
2. **Configure DNS** in your platform
3. **Add CNAME record** pointing to your app
4. **Enable SSL** (usually automatic)

### SSL Certificate

Most platforms provide free SSL:
- Heroku: Automatic with paid dynos
- Railway: Automatic
- Render: Automatic
- PythonAnywhere: Available on paid plans

## 🎯 Post-Deployment

After deploying:

1. **Test all features** in production
2. **Check error logs** for issues
3. **Monitor performance** metrics
4. **Set up backups** for database
5. **Configure alerts** for downtime
6. **Document** your deployment process
7. **Share** your live URL!

## 🆘 Troubleshooting

### App won't start
- Check logs: `heroku logs --tail`
- Verify environment variables
- Check Procfile syntax

### Database connection fails
- Verify MONGO_URI is correct
- Check IP whitelist in MongoDB Atlas
- Ensure database user has permissions

### Static files not loading
- Check static file paths
- Verify STATIC_URL configuration
- Consider using CDN

### Performance issues
- Enable caching
- Optimize database queries
- Use connection pooling
- Scale up resources

## 📚 Resources

- [Flask Deployment Docs](https://flask.palletsprojects.com/en/latest/deploying/)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [Heroku Python Docs](https://devcenter.heroku.com/categories/python-support)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

---

**Good luck with your deployment! 🚀**
