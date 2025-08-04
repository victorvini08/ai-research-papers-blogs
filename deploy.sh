#!/bin/bash

echo "🚀 AI Research Papers Daily - Deployment Script"
echo "================================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo "✅ Git repository initialized"
    echo ""
    echo "⚠️  IMPORTANT: Please create a GitHub repository and run:"
    echo "   git remote add origin https://github.com/yourusername/ai-research-papers-daily.git"
    echo "   git push -u origin main"
    echo ""
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Deployment Files Created:"
echo "   ✅ requirements.txt - Python dependencies"
echo "   ✅ render.yaml - Render.com configuration"
echo "   ✅ Procfile - Heroku/Railway configuration"
echo "   ✅ runtime.txt - Python version"
echo "   ✅ DEPLOYMENT.md - Complete deployment guide"
echo ""

echo "🌐 Deployment Options:"
echo ""
echo "1. 🚀 Render.com (Recommended - Free):"
echo "   - Go to https://render.com"
echo "   - Sign up and connect your GitHub"
echo "   - Click 'New Web Service'"
echo "   - Select your repository"
echo "   - Deploy automatically!"
echo ""

echo "2. 🚂 Railway.app (Alternative - Free):"
echo "   - Go to https://railway.app"
echo "   - Sign up and connect your GitHub"
echo "   - Deploy with one click"
echo ""

echo "3. 🏗️  Heroku (Paid):"
echo "   - Install Heroku CLI"
echo "   - Run: heroku create your-app-name"
echo "   - Run: git push heroku main"
echo ""

echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "🎉 Your app is ready for deployment!"
echo "   Local URL: http://localhost:5000"
echo "   Blog List: http://localhost:5000/blog"
echo "" 