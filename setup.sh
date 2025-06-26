#!/bin/bash

# 🚀 OSINT-AI Platform - Quick Start Script

set -e

echo "🔍 Initializing OSINT-AI Platform..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3.9+ is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) ]]; then
    print_error "Python 3.9+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js 16+ is required but not installed"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [[ $NODE_VERSION -lt 16 ]]; then
    print_error "Node.js 16+ is required. Current version: $NODE_VERSION"
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL not found. Please install and configure PostgreSQL"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    print_warning "Redis not found. Please install and configure Redis"
fi

print_success "Prerequisites check completed"

# Setup environment variables
print_status "Setting up environment variables..."

if [ ! -f .env ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file with your configuration"
else
    print_warning ".env file already exists"
fi

# Setup backend
print_status "Setting up backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r ../requirements.txt
print_success "Python dependencies installed"

# Setup database
print_status "Setting up database..."
if command -v psql &> /dev/null; then
    # Check if database exists
    DB_NAME="osint_ai_db"
    DB_USER="osint_user"
    
    if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME 2>/dev/null; then
        print_warning "Database $DB_NAME already exists"
    else
        print_status "Creating database and user..."
        
        # This would need to be run with proper PostgreSQL permissions
        # For now, just show the commands
        print_warning "Please run these commands manually in PostgreSQL:"
        echo "CREATE DATABASE $DB_NAME;"
        echo "CREATE USER $DB_USER WITH PASSWORD 'osint_pass';"
        echo "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    fi
else
    print_warning "PostgreSQL not available. Please set up database manually"
fi

cd ..

# Setup frontend
print_status "Setting up frontend..."

cd frontend

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
else
    print_warning "Node.js dependencies already installed"
fi

cd ..

# Create startup scripts
print_status "Creating startup scripts..."

# Backend startup script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "🚀 Starting OSINT-AI Backend on http://localhost:8000"
python main.py
EOF

# Frontend startup script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "🚀 Starting OSINT-AI Frontend on http://localhost:3000"
npm run dev
EOF

# Combined startup script
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting OSINT-AI Platform..."

# Start backend in background
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Start frontend in background
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interruption
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

# Make scripts executable
chmod +x start-backend.sh start-frontend.sh start-all.sh

print_success "Startup scripts created"

# Setup development tools
print_status "Setting up development tools..."

# Pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    cd backend
    source venv/bin/activate
    pre-commit install
    cd ..
    print_success "Pre-commit hooks installed"
fi

# Create development database migration
print_status "Creating database migrations..."
cd backend
source venv/bin/activate

# This would run Alembic migrations if configured
# For now, just create the tables directly
python -c "
from database import init_db
init_db()
print('Database tables created')
" 2>/dev/null || print_warning "Could not initialize database. Please check configuration."

cd ..

# Final setup
print_status "Final setup..."

# Create logs directory
mkdir -p logs

# Create uploads directory (for file uploads)
mkdir -p uploads

# Set proper permissions
chmod 755 logs uploads

print_success "Setup completed!"

echo ""
echo "🎉 OSINT-AI Platform Setup Complete!"
echo "====================================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your API keys and database configuration"
echo "2. Start PostgreSQL and Redis services"
echo "3. Run database migrations (if needed)"
echo "4. Start the platform:"
echo ""
echo "   # Start everything:"
echo "   ./start-all.sh"
echo ""
echo "   # Or start individually:"
echo "   ./start-backend.sh    # Backend API"
echo "   ./start-frontend.sh   # Frontend UI"
echo ""
echo "📊 URLs:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
echo "📖 Documentation:"
echo "   • README.md for detailed setup"
echo "   • .env.example for environment variables"
echo "   • API documentation at /docs endpoint"
echo ""
echo "🔒 Default admin credentials:"
echo "   • Email: admin@osint-ai.com"
echo "   • Password: (set in .env file)"
echo ""
print_success "Happy investigating! 🕵️‍♂️"
