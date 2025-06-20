#!/bin/bash

# Script de déploiement C2 Server pour VPS
echo "🎯 Déploiement du serveur C2 pour Red Team..."

# Variables
DOMAIN="your-c2-domain.com"
PROJECT_DIR="/var/www/c2-server"
C2_PORT="5000"
ADMIN_PASSWORD="C2Admin$(openssl rand -base64 12)"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Bannière de sécurité
echo "==============================================="
echo "🛡️ SERVEUR C2 POUR TESTS DE SÉCURITÉ LÉGAUX"
echo "⚠️ Usage autorisé uniquement pour:"
echo "   • Tests de sécurité internes"
echo "   • Exercices Red Team autorisés"
echo "   • Recherche en cybersécurité"
echo "==============================================="

read -p "Confirmez-vous l'usage légal et autorisé? (oui/non): " confirm
if [[ $confirm != "oui" && $confirm != "yes" ]]; then
    print_error "Usage non confirmé. Arrêt du déploiement."
    exit 1
fi

# Vérification des privilèges
if [[ $EUID -eq 0 ]]; then
   print_error "Ce script ne doit pas être exécuté en tant que root"
   exit 1
fi

print_status "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

print_status "Installation des dépendances système..."
sudo apt install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    sqlite3 \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    htop \
    screen

# Configuration du firewall
print_status "Configuration du firewall sécurisé..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow $C2_PORT/tcp
sudo ufw --force enable

# Configuration fail2ban
print_status "Configuration de fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
EOF

sudo systemctl restart fail2ban

# Création du répertoire projet
print_status "Configuration du projet C2..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Copie des fichiers
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# Configuration de l'environnement Python
print_status "Configuration de l'environnement Python..."
python3 -m venv c2_venv
source c2_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Génération des clés de sécurité
print_status "Génération des clés de sécurité..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Configuration des variables d'environnement
cat > .env << EOF
# Configuration C2 Server
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
DEBUG=False

# Configuration serveur
HOST=127.0.0.1
PORT=$C2_PORT

# Configuration admin
DEFAULT_ADMIN_PASSWORD=$ADMIN_PASSWORD

# Base de données
DB_PATH=$PROJECT_DIR/c2_server.db

# Sécurité
ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:$C2_PORT

# Logs
LOG_LEVEL=INFO
EOF

# Configuration Nginx pour C2
print_status "Configuration Nginx..."
sudo tee /etc/nginx/sites-available/c2-server > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirection HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # Configuration SSL (à configurer avec certbot)
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Sécurité SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
    
    # Headers de sécurité
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Limitation du taux de requêtes
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=3r/m;
    
    # Proxy vers l'application Flask
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:$C2_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Protection du login
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        
        proxy_pass http://127.0.0.1:$C2_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Logs sécurisés
    access_log /var/log/nginx/c2-server-access.log;
    error_log /var/log/nginx/c2-server-error.log;
}
EOF

# Activation du site
sudo ln -sf /etc/nginx/sites-available/c2-server /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Service systemd pour C2
print_status "Configuration du service C2..."
sudo tee /etc/systemd/system/c2-server.service > /dev/null <<EOF
[Unit]
Description=C2 Server for Red Team Operations
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/c2_venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/c2_venv/bin/python c2_server.py
Restart=always
RestartSec=3

# Sécurité du service
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Configuration des permissions
print_status "Configuration des permissions..."
sudo chown -R $USER:$USER $PROJECT_DIR
chmod 600 $PROJECT_DIR/.env
chmod +x $PROJECT_DIR/c2_agent.py

# Activation des services
print_status "Activation des services..."
sudo systemctl daemon-reload
sudo systemctl enable c2-server
sudo systemctl start c2-server
sudo systemctl restart nginx

# Script de monitoring
print_status "Création des scripts de maintenance..."
cat > $PROJECT_DIR/monitor.sh << 'EOF'
#!/bin/bash
echo "🎯 Monitoring C2 Server"
echo "========================"

echo "📊 Statut des services:"
systemctl is-active c2-server && echo "✅ C2 Server: Actif" || echo "❌ C2 Server: Inactif"
systemctl is-active nginx && echo "✅ Nginx: Actif" || echo "❌ Nginx: Inactif"

echo ""
echo "📈 Statistiques système:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "RAM: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "Disque: $(df -h / | awk 'NR==2{print $5}')"

echo ""
echo "🔍 Connexions actives:"
netstat -an | grep :5000 | wc -l

echo ""
echo "📝 Dernières activités (5 dernières lignes):"
tail -5 /var/log/nginx/c2-server-access.log
EOF

chmod +x $PROJECT_DIR/monitor.sh

# Script de sauvegarde
cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/c2-server"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /var/www/c2-server/c2_server.db $BACKUP_DIR/c2_server_$DATE.db

# Garder seulement les 14 dernières sauvegardes
find $BACKUP_DIR -name "c2_server_*.db" -type f -mtime +14 -delete

echo "✅ Sauvegarde créée: $BACKUP_DIR/c2_server_$DATE.db"
EOF

chmod +x $PROJECT_DIR/backup.sh

# Crontab pour la sauvegarde
(crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh") | crontab -

# Vérification finale
print_status "Vérification de l'installation..."
sleep 5

if systemctl is-active --quiet c2-server; then
    print_status "✅ Serveur C2 actif"
else
    print_error "❌ Serveur C2 inactif"
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx actif"
else
    print_error "❌ Nginx inactif"
fi

# Configuration SSL optionnelle
print_warning "Configuration SSL avec Let's Encrypt..."
read -p "Configurer SSL maintenant? (y/n): " ssl_choice
if [[ $ssl_choice == "y" || $ssl_choice == "Y" ]]; then
    sudo certbot --nginx -d $DOMAIN
fi

echo ""
echo "🎉 Déploiement du serveur C2 terminé!"
echo "=================================="
echo "🌐 URL: https://$DOMAIN (ou http://localhost:$C2_PORT)"
echo "🔑 Admin: admin"
echo "🔐 Password: $ADMIN_PASSWORD"
echo "📊 Monitoring: $PROJECT_DIR/monitor.sh"
echo "💾 Sauvegarde: $PROJECT_DIR/backup.sh"
echo ""
echo "📝 Commandes utiles:"
echo "   • Statut: sudo systemctl status c2-server"
echo "   • Logs: sudo journalctl -u c2-server -f"
echo "   • Monitoring: $PROJECT_DIR/monitor.sh"
echo "   • Redémarrer: sudo systemctl restart c2-server"
echo ""
print_warning "🛡️ USAGE LÉGAL UNIQUEMENT - Documentez vos tests!"
print_warning "🔒 Changez le mot de passe admin après la première connexion"
