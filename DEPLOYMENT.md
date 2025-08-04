# Deployment Guide - AI Research Papers Daily

This guide will help you deploy your AI Research Papers Daily application to make it accessible online.

## 🚀 Quick Deploy Options

### Option 1: Render.com (Recommended - Free)

1. **Sign up for Render.com**
   - Go to [render.com](https://render.com)
   - Create a free account

2. **Connect your GitHub repository**
   - Push your code to GitHub
   - Connect your GitHub account to Render

3. **Deploy automatically**
   - Render will detect the `render.yaml` file
   - Click "New Web Service"
   - Select your repository
   - Render will automatically configure everything

4. **Your app will be live at:**
   - `https://your-app-name.onrender.com`

### Option 2: Railway.app (Alternative - Free tier)

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Create a free account

2. **Deploy from GitHub**
   - Connect your GitHub repository
   - Railway will automatically detect it's a Python app
   - Deploy with one click

3. **Your app will be live at:**
   - `https://your-app-name.railway.app`

### Option 3: Heroku (Paid)

1. **Sign up for Heroku**
   - Go to [heroku.com](https://heroku.com)
   - Create an account

2. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from heroku.com
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## 📁 Files for Deployment

The following files are included for deployment:

- `requirements.txt` - Python dependencies
- `render.yaml` - Render.com configuration
- `Procfile` - Heroku/Railway configuration
- `runtime.txt` - Python version specification
- `main.py` - Application entry point

## 🔧 Environment Variables

You may want to set these environment variables in your deployment platform:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_PATH=database/papers.db
```

## 📊 Database Considerations

**Important:** The current setup uses SQLite, which is fine for development but has limitations for production:

1. **SQLite limitations:**
   - Data is stored in files (not persistent across deployments)
   - Limited concurrent access
   - Not suitable for high traffic

2. **For production, consider:**
   - PostgreSQL (recommended)
   - MySQL
   - MongoDB

## 🚀 Deployment Steps

### Step 1: Prepare Your Code

1. **Test locally first:**
   ```bash
   python main.py
   ```

2. **Create a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/ai-research-papers-daily.git
   git push -u origin main
   ```

### Step 2: Deploy to Render.com

1. **Go to Render Dashboard**
2. **Click "New Web Service"**
3. **Connect your GitHub repository**
4. **Configure:**
   - Name: `ai-research-papers-daily`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. **Click "Create Web Service"**

### Step 3: Configure Environment Variables

In your Render dashboard:
1. Go to your service
2. Click "Environment"
3. Add these variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here
   ```

### Step 4: Test Your Deployment

1. **Wait for deployment to complete**
2. **Visit your app URL**
3. **Test all features:**
   - Home page
   - Blog list
   - Individual blog posts
   - Archive

## 🔄 Continuous Deployment

Once deployed, your app will automatically update when you push changes to GitHub.

## 📈 Monitoring

- **Render Dashboard:** Monitor logs and performance
- **Uptime:** Check if your app is running
- **Logs:** Debug any issues

## 🛠️ Troubleshooting

### Common Issues:

1. **Build fails:**
   - Check `requirements.txt` for correct dependencies
   - Ensure all imports are correct

2. **App crashes:**
   - Check logs in your deployment platform
   - Verify database path is correct

3. **Database issues:**
   - Consider switching to PostgreSQL for production
   - Check file permissions

## 🌐 Custom Domain (Optional)

1. **Buy a domain** (e.g., from Namecheap, GoDaddy)
2. **Configure DNS** to point to your deployment URL
3. **Add custom domain** in your deployment platform

## 📱 Next Steps

After deployment:

1. **Set up automatic paper fetching**
2. **Configure daily blog generation**
3. **Add monitoring and analytics**
4. **Optimize for performance**

## 🆘 Support

If you encounter issues:

1. Check the deployment platform logs
2. Verify all files are committed to GitHub
3. Test locally first
4. Check environment variables

---

**Your AI Research Papers Daily app will be live and accessible to the world! 🌍✨** 