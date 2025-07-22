# 🚀 Receipt Analyzer Deployment Guide

This guide will help you deploy your Receipt & Bill Analyzer application to production.

## 📋 **Prerequisites**

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Railway Account**: For backend deployment (free tier available)
3. **Streamlit Cloud Account**: For frontend deployment (free tier available)

## 🔧 **Backend Deployment (Django)**

### Option 1: Railway (Recommended)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway Project**:
   ```bash
   railway init
   ```

4. **Deploy to Railway**:
   ```bash
   railway up
   ```

5. **Get your backend URL**:
   ```bash
   railway domain
   ```

### Option 2: Render

1. **Go to [Render.com](https://render.com)**
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Build Command**: `pip install -r requirements-backend.txt && python receipt_analyzer/manage.py migrate`
   - **Start Command**: `gunicorn receipt_analyzer.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3.11

### Option 3: Heroku

1. **Install Heroku CLI**:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Deploy to Heroku**:
   ```bash
   git push heroku main
   ```

## 🎨 **Frontend Deployment (Streamlit)**

### Streamlit Cloud Deployment

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Deploy your app**:
   - **Repository**: Your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **Requirements file**: `requirements-frontend.txt`

4. **Configure environment variables**:
   - `API_BASE_URL`: Your backend URL (e.g., `https://your-app.railway.app/api`)

## 🔗 **Connect Frontend to Backend**

1. **Update API URL in Streamlit app**:
   ```python
   # In streamlit_app.py, line ~15
   API_BASE_URL = "https://your-backend-url.railway.app/api"
   ```

2. **Test the connection**:
   - Upload a receipt in the Streamlit app
   - Check if data is saved in the backend

## 📊 **Environment Variables**

### Backend Environment Variables (Railway/Render/Heroku)

```bash
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Frontend Environment Variables (Streamlit Cloud)

```bash
API_BASE_URL=https://your-backend-url.railway.app/api
```

## 🧪 **Testing Deployment**

1. **Test Backend**:
   ```bash
   curl https://your-backend-url.railway.app/api/health/
   ```

2. **Test Frontend**:
   - Visit your Streamlit app URL
   - Upload a test receipt
   - Check if data appears in the records

## 🔧 **Troubleshooting**

### Common Issues

1. **Backend not starting**:
   - Check logs: `railway logs` or `heroku logs`
   - Verify `Procfile` exists
   - Check `requirements-backend.txt`

2. **Frontend can't connect to backend**:
   - Verify `API_BASE_URL` is correct
   - Check CORS settings in Django
   - Test backend URL directly

3. **Database issues**:
   - Run migrations: `python manage.py migrate`
   - Check database URL format

### Debug Commands

```bash
# Railway
railway logs
railway status

# Heroku
heroku logs --tail
heroku run python manage.py migrate

# Local testing
python receipt_analyzer/manage.py runserver
streamlit run streamlit_app.py
```

## 📈 **Monitoring**

1. **Railway Dashboard**: Monitor backend performance
2. **Streamlit Cloud**: Monitor frontend usage
3. **Application Logs**: Check for errors and usage patterns

## 🔒 **Security Considerations**

1. **Environment Variables**: Never commit secrets to Git
2. **CORS Settings**: Configure properly for production
3. **Database**: Use production database (PostgreSQL)
4. **SSL**: Ensure HTTPS is enabled

## 🎉 **Success Checklist**

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] API connection working
- [ ] File uploads working
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] SSL certificates active
- [ ] Error monitoring set up

---

**Need Help?** Check the logs and error messages for specific issues. Most deployment problems are related to environment variables or missing dependencies. 