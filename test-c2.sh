#!/bin/bash

# Script de test du serveur C2
echo "🧪 Test du serveur C2..."

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅ OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
}

# Variables
SERVER_URL="http://localhost:5000"
TEST_DIR="/tmp/c2_test"

# Bannière de sécurité
echo "============================================="
echo "🛡️ TEST DU SERVEUR C2 - USAGE LÉGAL UNIQUEMENT"
echo "============================================="

# Test 1: Démarrage du serveur C2
print_test "Démarrage du serveur C2 en mode test..."

cd /workspaces/abdou.github.io

# Installer les dépendances si nécessaire
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors flask-jwt-extended flask-socketio python-socketio requests psutil cryptography bcrypt python-dotenv > /dev/null 2>&1
else
    source venv/bin/activate
fi

# Démarrer le serveur en arrière-plan
python3 c2_server.py &
SERVER_PID=$!
sleep 8

# Test 2: Health check
print_test "Test de connectivité du serveur..."
if curl -s "$SERVER_URL" | grep -q "C2 Server"; then
    print_success "Serveur accessible"
else
    print_error "Serveur inaccessible"
fi

# Test 3: API d'authentification
print_test "Test de l'API d'authentification..."
AUTH_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"C2Admin123!"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    print_success "Authentification OK"
    TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    print_error "Authentification échouée"
    TOKEN=""
fi

# Test 4: API des agents
print_test "Test de l'API des agents..."
if [ -n "$TOKEN" ]; then
    AGENTS_RESPONSE=$(curl -s "$SERVER_URL/api/agents" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$AGENTS_RESPONSE" | grep -q "agents"; then
        print_success "API agents OK"
    else
        print_error "API agents échouée"
    fi
else
    print_error "Test API agents ignoré (pas de token)"
fi

# Test 5: Enregistrement d'agent
print_test "Test d'enregistrement d'agent..."
REGISTER_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/agent/register" \
    -H "Content-Type: application/json" \
    -d '{
        "hostname": "test-host",
        "username": "test-user",
        "os_info": "Linux Test",
        "capabilities": ["test"]
    }')

if echo "$REGISTER_RESPONSE" | grep -q "agent_id"; then
    print_success "Enregistrement agent OK"
    AGENT_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['agent_id'])")
else
    print_error "Enregistrement agent échoué"
    AGENT_ID=""
fi

# Test 6: Check-in d'agent
print_test "Test de check-in d'agent..."
if [ -n "$AGENT_ID" ]; then
    CHECKIN_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/agent/$AGENT_ID/checkin")
    
    if echo "$CHECKIN_RESPONSE" | grep -q "status"; then
        print_success "Check-in agent OK"
    else
        print_error "Check-in agent échoué"
    fi
else
    print_error "Test check-in ignoré (pas d'agent ID)"
fi

# Test 7: Envoi de commande
print_test "Test d'envoi de commande..."
if [ -n "$TOKEN" ] && [ -n "$AGENT_ID" ]; then
    COMMAND_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/agents/$AGENT_ID/commands" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"command": "whoami"}')
    
    if echo "$COMMAND_RESPONSE" | grep -q "success"; then
        print_success "Envoi de commande OK"
    else
        print_error "Envoi de commande échoué"
    fi
else
    print_error "Test commande ignoré (token ou agent manquant)"
fi

# Test 8: Statistiques
print_test "Test des statistiques..."
if [ -n "$TOKEN" ]; then
    STATS_RESPONSE=$(curl -s "$SERVER_URL/api/stats" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$STATS_RESPONSE" | grep -q "agents"; then
        print_success "Statistiques OK"
    else
        print_error "Statistiques échouées"
    fi
else
    print_error "Test stats ignoré (pas de token)"
fi

# Test 9: Test de l'agent client
print_test "Test de l'agent client en mode test..."
if [ -f "c2_agent.py" ]; then
    timeout 30 python3 c2_agent.py --server "$SERVER_URL" --test &
    AGENT_PID=$!
    sleep 15
    
    if ps -p $AGENT_PID > /dev/null; then
        print_success "Agent client fonctionnel"
        kill $AGENT_PID 2>/dev/null
    else
        print_error "Agent client défaillant"
    fi
else
    print_error "Agent client non trouvé"
fi

# Test 10: Vérification de la base de données
print_test "Test de la base de données..."
if [ -f "c2_server.db" ]; then
    TABLES=$(sqlite3 c2_server.db ".tables")
    if echo "$TABLES" | grep -q "agents"; then
        print_success "Base de données OK"
    else
        print_error "Tables manquantes dans la DB"
    fi
else
    print_error "Base de données non créée"
fi

# Test 11: Vérification des fichiers de configuration
print_test "Vérification des fichiers..."

required_files=("c2_server.py" "c2_agent.py" "templates/index.html" "templates/admin.html" "deploy-c2.sh")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Fichier $file présent"
    else
        print_error "Fichier $file manquant"
    fi
done

# Test 12: Test de sécurité basique
print_test "Test de sécurité basique..."
SECURITY_RESPONSE=$(curl -s "$SERVER_URL/api/agents" \
    -H "Authorization: Bearer invalid-token")

if echo "$SECURITY_RESPONSE" | grep -q "error\|Unauthorized\|401"; then
    print_success "Protection par token OK"
else
    print_error "Protection par token défaillante"
fi

# Nettoyage
print_test "Nettoyage..."
kill $SERVER_PID 2>/dev/null
deactivate 2>/dev/null

echo ""
echo "🎯 Tests terminés!"
echo ""
echo "📋 Pour déployer en production:"
echo "1. Configurez votre VPS/serveur"
echo "2. Modifiez les variables dans deploy-c2.sh"
echo "3. Exécutez: ./deploy-c2.sh"
echo "4. Accédez à https://votre-domaine.com/admin"
echo ""
echo "🔧 Pour tester localement:"
echo "1. python3 c2_server.py"
echo "2. Ouvrez http://localhost:5000/admin"
echo "3. Login: admin / C2Admin123!"
echo "4. Dans un autre terminal: python3 c2_agent.py --test"
echo ""
echo "⚠️ RAPPEL: USAGE LÉGAL UNIQUEMENT - Tests autorisés seulement!"
