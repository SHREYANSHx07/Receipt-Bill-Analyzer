#!/bin/bash

echo "🚀 Receipt & Bill Analyzer Deployment Script"
echo "=============================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if repository is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Receipt & Bill Analyzer"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Deploy to Streamlit Cloud (Frontend only)"
echo "2. Deploy to Railway (Backend)"
echo "3. Deploy to Render (Backend)"
echo "4. Deploy to Heroku (Backend)"
echo "5. Deploy both frontend and backend"
echo ""

read -p "Choose deployment option (1-5): " choice

case $choice in
    1)
        echo "🎯 Deploying to Streamlit Cloud..."
        echo "📝 Steps:"
        echo "1. Push your code to GitHub"
        echo "2. Go to https://share.streamlit.io"
        echo "3. Connect your GitHub repository"
        echo "4. Set main file path: streamlit_app.py"
        echo "5. Add environment variable: API_BASE_URL"
        echo ""
        echo "💡 Don't forget to deploy your backend separately!"
        ;;
    2)
        echo "🚂 Deploying to Railway..."
        echo "📝 Steps:"
        echo "1. Go to https://railway.app"
        echo "2. Connect your GitHub repository"
        echo "3. Add environment variables:"
        echo "   - DJANGO_SETTINGS_MODULE=receipt_analyzer.settings"
        echo "   - DATABASE_URL=sqlite:///db.sqlite3"
        echo "4. Deploy!"
        ;;
    3)
        echo "🎨 Deploying to Render..."
        echo "📝 Steps:"
        echo "1. Go to https://render.com"
        echo "2. Create new Web Service"
        echo "3. Connect your GitHub repository"
        echo "4. Set build command: pip install -r requirements.txt"
        echo "5. Set start command: python manage.py runserver 0.0.0.0:\$PORT"
        echo "6. Deploy!"
        ;;
    4)
        echo "🦸 Deploying to Heroku..."
        echo "📝 Steps:"
        echo "1. Install Heroku CLI"
        echo "2. Run: heroku create your-app-name"
        echo "3. Run: git push heroku main"
        echo "4. Set environment variables in Heroku dashboard"
        ;;
    5)
        echo "🌐 Deploying both frontend and backend..."
        echo "📝 Recommended approach:"
        echo "1. Deploy backend to Railway/Render/Heroku"
        echo "2. Get your backend URL"
        echo "3. Deploy frontend to Streamlit Cloud"
        echo "4. Set API_BASE_URL environment variable"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 For detailed instructions, see README_DEPLOYMENT.md"
echo "🎉 Happy deploying!" 