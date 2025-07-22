# 🚀 Streamlit Cloud Deployment Guide

## 📋 Prerequisites

1. **GitHub Account**: You need a GitHub account to host your code
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Backend API**: Your Django backend needs to be deployed separately

## 🔧 Backend Deployment Options

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables:
   ```
   DJANGO_SETTINGS_MODULE=receipt_analyzer.settings
   DATABASE_URL=sqlite:///db.sqlite3
   ```
4. Deploy your Django backend

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python manage.py runserver 0.0.0.0:$PORT`

### Option 3: Heroku
1. Create a `Procfile`:
   ```
   web: python manage.py runserver 0.0.0.0:$PORT
   ```
2. Deploy to Heroku using their CLI or dashboard

## 🎯 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **File Structure**: Ensure your repository has this structure:
   ```
   your-repo/
   ├── streamlit_app.py          # Main Streamlit app
   ├── requirements.txt           # Python dependencies
   ├── .streamlit/
   │   └── config.toml          # Streamlit config
   ├── receipt_analyzer/         # Django backend (if included)
   └── README.md
   ```

2. **Environment Variables**: Update `streamlit_app.py` to use environment variables:
   ```python
   API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Push to GitHub**: Commit and push your code to GitHub
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the main file path: `streamlit_app.py`
   - Click "Deploy!"

### Step 3: Configure Environment Variables

In Streamlit Cloud dashboard:
1. Go to your app settings
2. Add environment variable:
   ```
   API_BASE_URL=https://your-backend-url.com/api
   ```

## 🔗 Connecting Frontend to Backend

### For Railway Backend:
```
API_BASE_URL=https://your-app-name.railway.app/api
```

### For Render Backend:
```
API_BASE_URL=https://your-app-name.onrender.com/api
```

### For Heroku Backend:
```
API_BASE_URL=https://your-app-name.herokuapp.com/api
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Backend Connection Error**:
   - Check if your backend is running
   - Verify the API_BASE_URL environment variable
   - Ensure CORS is configured in Django

2. **Import Errors**:
   - Make sure all dependencies are in `requirements.txt`
   - Check Python version compatibility

3. **File Upload Issues**:
   - Ensure file size limits are appropriate
   - Check file type validation

### Debugging:

1. **Check Logs**: Streamlit Cloud provides logs in the dashboard
2. **Test Locally**: Test with `streamlit run streamlit_app.py`
3. **API Testing**: Use tools like Postman to test your backend API

## 📊 Monitoring

- **Streamlit Cloud**: Monitor app performance in the dashboard
- **Backend**: Check your backend provider's monitoring tools
- **Logs**: Review logs for errors and performance issues

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **CORS**: Configure CORS properly in Django
3. **File Uploads**: Implement proper validation and sanitization
4. **API Keys**: Use environment variables for any API keys

## 🚀 Production Checklist

- [ ] Backend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] File upload limits set
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Performance optimized
- [ ] Security measures in place

## 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud documentation
2. Review your backend provider's documentation
3. Check GitHub issues for similar problems
4. Test locally before deploying

## 🎉 Success!

Once deployed, your app will be available at:
```
https://your-app-name.streamlit.app
```

Share this URL with others to use your Receipt & Bill Analyzer! 