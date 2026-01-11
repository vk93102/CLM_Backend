#!/bin/bash

##############################################################################
# CLM Backend - Quick Start Testing Guide
# Run this script to setup and test all API endpoints
##############################################################################

set -e

BASE_DIR="/Users/vishaljha/Desktop/CLM_Backend"
cd "$BASE_DIR"

echo "=========================================="
echo "CLM Backend - Setup & Testing"
echo "=========================================="
echo ""

# Check if Django is running
echo "1️⃣  Checking if Django server is running on port 8888..."
if ! curl -s http://localhost:8888/api/auth/login/ > /dev/null 2>&1; then
    echo "❌ Django server is NOT running on port 8888"
    echo ""
    echo "Starting Django server..."
    echo ""
    python manage.py runserver 0.0.0.0:8888 &
    SERVER_PID=$!
    sleep 3
    echo "✓ Django server started (PID: $SERVER_PID)"
    echo ""
else
    echo "✓ Django server is running"
    echo ""
fi

# Run database migrations if needed
echo "2️⃣  Checking database..."
python manage.py migrate --noinput > /dev/null 2>&1 && echo "✓ Database is up to date" || echo "⚠ Database update attempted"
echo ""

# Run API endpoint tests
echo "3️⃣  Running API endpoint tests..."
echo ""
bash test_endpoints.sh

echo ""
echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo "   - Check test results above"
echo "   - Review API responses"
echo "   - Fix any failing endpoints"
echo ""
echo "🌐 Access Application:"
echo "   - API: http://localhost:8888/api/"
echo "   - Admin: http://localhost:8888/admin/"
echo ""
