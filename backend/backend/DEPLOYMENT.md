# Backend Deployment Guide

Your Flask backend is now ready for deployment! Here are several deployment options:

## 🚀 Quick Deploy Options (Recommended)

### 1. Railway (Easiest & Free Tier)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   cd backend/
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables:**
   ```bash
   railway variables set API_KEY=your_actual_api_key_here
   railway variables set SUBGRAPH_URL=https://api.studio.thegraph.com/query/121751/eth-new-delhi/version/latest
   ```

4. **Get your deployed URL:**
   ```bash
   railway status
   ```

### 2. Render (Free Tier Available)

1. **Connect GitHub:**
   - Push your code to GitHub
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --host 0.0.0.0 --port $PORT --workers 4 main:app`

3. **Environment Variables:**
   ```
   API_KEY=your_actual_api_key_here
   SUBGRAPH_URL=https://api.studio.thegraph.com/query/121751/eth-new-delhi/version/latest
   FLASK_ENV=production
   ```

### 3. Heroku

1. **Install Heroku CLI:**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Deploy:**
   ```bash
   cd backend/
   heroku create your-app-name
   git init
   git add .
   git commit -m "Initial deploy"
   heroku git:remote -a your-app-name
   git push heroku main
   ```

3. **Set Environment Variables:**
   ```bash
   heroku config:set API_KEY=your_actual_api_key_here
   heroku config:set SUBGRAPH_URL=https://api.studio.thegraph.com/query/121751/eth-new-delhi/version/latest
   ```

## 🐳 Docker Deployment

### Local Docker
```bash
cd backend/
docker build -t substream-backend .
docker run -p 8080:8080 -e API_KEY=your_key substream-backend
```

### Docker Hub + Any VPS
```bash
# Build and push
docker build -t your-username/substream-backend .
docker push your-username/substream-backend

# Deploy on any server
docker pull your-username/substream-backend
docker run -d -p 80:8080 -e API_KEY=your_key your-username/substream-backend
```

## 🔧 Environment Variables You Need

For any deployment, set these environment variables:

```bash
API_KEY=2288df215e46f0fa1ebdd0046bdc6746  # Your actual API key
SUBGRAPH_URL=https://api.studio.thegraph.com/query/121751/eth-new-delhi/version/latest
FLASK_ENV=production
FLASK_DEBUG=False
```

## 📋 Testing Your Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-app-url.com/health

# Query with contract address
curl https://your-app-url.com/query/0x1234567890123456789012345678901234567890
```

## 💡 Tips

- **Railway** is the easiest for beginners
- **Render** has good free tier limits
- **Heroku** requires credit card but has good documentation
- **Docker** gives you most control and can deploy anywhere

## 🚨 Security Notes

1. **Never commit your actual API key** to version control
2. **Use environment variables** for all sensitive data
3. **Consider rate limiting** for production use
4. **Enable HTTPS** (most platforms do this automatically)

## 📊 Monitoring

Your app includes a `/health` endpoint for monitoring. Most platforms will automatically use this for health checks.

Choose the platform that best fits your needs and budget!