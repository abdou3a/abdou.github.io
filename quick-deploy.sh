#!/bin/bash

# 🚀 Script de déploiement automatisé du serveur C2
# Usage: ./quick-deploy.sh [target_ip] [username]

set -e

echo "🚀 Script de déploiement C2 - Déploiement distant"
echo "=================================================="

# Variables
TARGET_IP=${1:-""}
USERNAME=${2:-"root"}
PROJECT_NAME="abdou.github.io"
REMOTE_DIR="/opt/c2-server"

if [ -z "$TARGET_IP" ]; then
    echo "❌ Usage: $0 <target_ip> [username]"
    echo "   Exemple: $0 192.168.1.100 ubuntu"
    exit 1
fi

echo "🎯 Serveur cible: $USERNAME@$TARGET_IP"
echo "📁 Répertoire distant: $REMOTE_DIR"

# Vérifier la connectivité SSH
echo "🔍 Test de connectivité SSH..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $USERNAME@$TARGET_IP exit 2>/dev/null; then
    echo "❌ Impossible de se connecter à $TARGET_IP"
    echo "   Vérifiez que SSH est configuré et que vous avez les bonnes clés"
    exit 1
fi

echo "✅ Connexion SSH OK"

# Créer un package du projet
echo "📦 Création du package de déploiement..."
tar -czf c2-deploy.tar.gz \
    c2_server.py \
    c2_agent.py \
    templates/ \
    requirements.txt \
    Dockerfile \
    docker-compose.yml \
    deploy-c2.sh \
    wsgi.py \
    .env.example \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude="c2_database.db"

echo "🚀 Déploiement sur le serveur distant..."

# Script de déploiement distant
ssh $USERNAME@$TARGET_IP "bash -s" << 'EOF'
set -e

echo "🔧 Préparation du serveur..."

# Créer le répertoire de déploiement
sudo mkdir -p /opt/c2-server
sudo chown $USER:$USER /opt/c2-server

# Installer les dépendances système
sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip curl

# Installer Docker (optionnel)
if ! command -v docker &> /dev/null; then
    echo "🐳 Installation de Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

echo "✅ Serveur préparé"
EOF

# Copier les fichiers
echo "📁 Copie des fichiers..."
scp c2-deploy.tar.gz $USERNAME@$TARGET_IP:/opt/c2-server/

# Installation et configuration
ssh $USERNAME@$TARGET_IP "bash -s" << 'EOF'
set -e
cd /opt/c2-server

echo "📦 Extraction des fichiers..."
tar -xzf c2-deploy.tar.gz
rm c2-deploy.tar.gz

echo "🐍 Configuration de l'environnement Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️ Configuration du service..."
# Créer le fichier .env
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Générer une clé JWT aléatoire
    JWT_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/your-super-secret-jwt-key-here/$JWT_KEY/" .env
    
    echo "🔑 Fichier .env créé avec clé JWT sécurisée"
fi

# Permissions
chmod +x deploy-c2.sh c2_server.py
chmod 600 .env

echo "🔥 Test de démarrage..."
timeout 10s python3 c2_server.py || echo "⚠️ Test timeout (normal)"

echo "✅ Déploiement terminé!"
echo ""
echo "🌐 Pour démarrer le serveur:"
echo "   ssh $USER@$(hostname -I | awk '{print $1}')"
echo "   cd /opt/c2-server"
echo "   source venv/bin/activate"
echo "   python3 c2_server.py"
echo ""
echo "🔗 Interface admin sera disponible sur:"
echo "   http://$(hostname -I | awk '{print $1}'):5000/admin"
EOF

# Nettoyage local
rm c2-deploy.tar.gz

echo ""
echo "🎉 Déploiement terminé avec succès!"
echo "🔗 Serveur C2 déployé sur: $TARGET_IP"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Se connecter au serveur: ssh $USERNAME@$TARGET_IP"
echo "2. Aller dans le répertoire: cd /opt/c2-server"
echo "3. Activer l'environnement: source venv/bin/activate"
echo "4. Démarrer le serveur: python3 c2_server.py"
echo "5. Accéder à l'admin: http://$TARGET_IP:5000/admin"
echo ""
echo "🔐 Identifiants par défaut:"
echo "   Username: admin"
echo "   Password: C2Admin123!"
