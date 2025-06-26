#!/bin/bash

# OSINT-AI Platform - Script de démarrage complet
# Ce script démarre tous les services nécessaires

set -e

echo "🔍 OSINT-AI Platform - Démarrage complet"
echo "========================================"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour vérifier si un service est en cours d'exécution
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        log_success "$service_name est accessible sur le port $port"
        return 0
    else
        log_warning "$service_name n'est pas accessible sur le port $port"
        return 1
    fi
}

# Vérifier les prérequis
log_info "Vérification des prérequis..."

# Vérifier Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION installé"
else
    log_error "Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    log_success "Node.js $NODE_VERSION installé"
else
    log_warning "Node.js n'est pas installé - le frontend ne pourra pas démarrer"
fi

# Vérifier Docker
if command -v docker &> /dev/null; then
    log_success "Docker installé"
else
    log_warning "Docker n'est pas installé - utilisation des services externes"
fi

# Étape 1: Démarrer les services de base (PostgreSQL, Redis)
log_info "Étape 1: Démarrage des services de base..."

if command -v docker &> /dev/null; then
    log_info "Démarrage de PostgreSQL et Redis avec Docker..."
    docker-compose -f docker-compose.dev.yml up -d
    
    # Attendre que les services soient prêts
    sleep 5
    
    # Vérifier PostgreSQL
    if docker exec osint-ai-postgres pg_isready -U osint_user > /dev/null 2>&1; then
        log_success "PostgreSQL est prêt"
    else
        log_error "PostgreSQL n'est pas prêt"
    fi
    
    # Vérifier Redis
    if docker exec osint-ai-redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis est prêt"
    else
        log_error "Redis n'est pas prêt"
    fi
else
    log_warning "Docker non disponible - assurez-vous que PostgreSQL et Redis sont installés"
fi

# Étape 2: Configurer et démarrer le backend
log_info "Étape 2: Configuration et démarrage du backend..."

# Vérifier l'environnement virtuel
if [ ! -d "osint_env" ]; then
    log_info "Création de l'environnement virtuel Python..."
    python3 -m venv osint_env
fi

# Activer l'environnement virtuel
source osint_env/bin/activate

# Installer les dépendances
log_info "Installation des dépendances Python..."
pip install -r requirements-basic.txt > /dev/null 2>&1
pip install email-validator python-whois dnspython numpy > /dev/null 2>&1

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    log_info "Création du fichier .env..."
    cp .env.example .env
    log_warning "Veuillez configurer le fichier .env avec vos paramètres"
fi

# Démarrer le backend en arrière-plan
log_info "Démarrage du serveur FastAPI..."
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Attendre que le backend soit prêt
sleep 5

if check_service "Backend API" 8000; then
    log_success "Backend démarré avec succès (PID: $BACKEND_PID)"
    echo $BACKEND_PID > backend.pid
else
    log_error "Échec du démarrage du backend"
    log_info "Vérifiez les logs: tail -f backend.log"
fi

# Étape 3: Configurer et démarrer le frontend
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    log_info "Étape 3: Configuration et démarrage du frontend..."
    
    cd frontend
    
    # Installer les dépendances
    if [ ! -d "node_modules" ]; then
        log_info "Installation des dépendances Node.js..."
        npm install > /dev/null 2>&1
    fi
    
    # Démarrer le frontend en arrière-plan
    log_info "Démarrage du serveur Next.js..."
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Attendre que le frontend soit prêt
    sleep 10
    
    if check_service "Frontend" 3000; then
        log_success "Frontend démarré avec succès (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > frontend.pid
    else
        log_warning "Frontend non accessible - vérifiez les logs: tail -f frontend.log"
    fi
else
    log_warning "Node.js/npm non disponible - frontend non démarré"
fi

# Résumé final
echo ""
log_info "🎉 Démarrage terminé!"
echo "========================================"
echo ""
log_info "Services disponibles:"

if check_service "PostgreSQL" 5432; then
    echo "  🗄️  PostgreSQL: localhost:5432"
fi

if check_service "Redis" 6379; then
    echo "  📦 Redis: localhost:6379"
fi

if check_service "Backend API" 8000; then
    echo "  🚀 Backend API: http://localhost:8000"
    echo "  📚 Documentation: http://localhost:8000/docs"
fi

if check_service "Frontend" 3000; then
    echo "  🌐 Frontend: http://localhost:3000"
fi

echo ""
log_info "Commandes utiles:"
echo "  📊 Logs backend: tail -f backend.log"
echo "  📊 Logs frontend: tail -f frontend.log"
echo "  🛑 Arrêter: ./stop_services.sh"
echo "  🔧 Status Docker: docker ps"
echo ""

# Créer un script d'arrêt
cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt des services OSINT-AI..."

# Arrêter les processus
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
    echo "✅ Backend arrêté"
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
    echo "✅ Frontend arrêté"
fi

# Arrêter Docker si disponible
if command -v docker &> /dev/null; then
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Services Docker arrêtés"
fi

echo "🎉 Tous les services sont arrêtés"
EOF

chmod +x stop_services.sh

log_success "Script d'arrêt créé: ./stop_services.sh"
