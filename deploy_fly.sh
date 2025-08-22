#!/bin/bash

# Fly.io Deployment Script for AI Research Papers Summarizer
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting Fly.io deployment..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   brew install flyctl"
    exit 1
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io. Please login first:"
    echo "   flyctl auth login"
    exit 1
fi

# Get the app name from fly.toml
APP_NAME=$(grep '^app = ' fly.toml | cut -d'"' -f2)
echo "📱 Deploying app: $APP_NAME"

# Create app if it doesn't exist
if ! flyctl apps list | grep -q "$APP_NAME"; then
    echo "🔧 Creating new app: $APP_NAME"
    flyctl apps create "$APP_NAME"
else
    echo "✅ App $APP_NAME already exists"
fi

# Create volume if it doesn't exist
if ! flyctl volumes list | grep -q "data"; then
    echo "💾 Creating persistent volume for SQLite database..."
    flyctl volumes create data --region sin --size 1
else
    echo "✅ Volume 'data' already exists"
fi

# Set required environment variables
echo "🔐 Setting environment variables..."

# Generate a random secret key if not already set
if ! flyctl secrets list | grep -q "SECRET_KEY"; then
    echo "🔑 Setting SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    flyctl secrets set SECRET_KEY="$SECRET_KEY"
else
    echo "✅ SECRET_KEY already set"
fi

# Check if GROQ_API_KEY is provided
if [ -n "$GROQ_API_KEY" ]; then
    echo "🤖 Setting GROQ_API_KEY..."
    flyctl secrets set GROQ_API_KEY="$GROQ_API_KEY"
else
    echo "⚠️  GROQ_API_KEY not provided. LLM summarization will use rule-based fallback."
fi

# Deploy the application
echo "🚀 Deploying application..."
flyctl deploy

# Allocate IP addresses
echo "🌐 Allocating IP addresses..."
flyctl ips allocate-v4
flyctl ips allocate-v6

# Get the allocated IPs
echo "📋 Allocated IP addresses:"
flyctl ips list

# Create SSL certificates
echo "🔒 Creating SSL certificates..."
flyctl certs create "$APP_NAME.fly.dev"
flyctl certs create "www.$APP_NAME.fly.dev"

# Show certificate status
echo "📜 Certificate status:"
flyctl certs list

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your app is available at: https://$APP_NAME.fly.dev"
echo ""
echo "📝 Next steps:"
echo "1. Wait for DNS propagation (usually 5-10 minutes)"
echo "2. Add your custom domain in GoDaddy DNS:"
echo "   - A record: @ -> [IPv4 from above]"
echo "   - AAAA record: @ -> [IPv6 from above]"
echo "   - CNAME: www -> @"
echo "3. Add custom domain in Fly.io:"
echo "   flyctl certs create ai-blogs.co.in"
echo "   flyctl certs create www.ai-blogs.co.in"
echo ""
echo "🔍 Check app status: flyctl status"
echo "📊 View logs: flyctl logs"
echo "🌐 Open app: flyctl open"
