#!/usr/bin/env python3
import os
import sys
import subprocess

# Changer vers le répertoire du projet
os.chdir('/workspaces/abdou.github.io')

# Supprimer la variable DATABASE_URL pour forcer SQLite
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

print("🚀 Démarrage du serveur OSINT-AI...")
print("📍 Répertoire:", os.getcwd())

try:
    # Démarrer le serveur avec uvicorn
    cmd = [sys.executable, '-m', 'uvicorn', 'backend.main_dev:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
    print("💻 Commande:", ' '.join(cmd))
    
    # Lancer le serveur
    subprocess.run(cmd)
    
except KeyboardInterrupt:
    print("\n⏹️  Serveur arrêté")
except Exception as e:
    print(f"❌ Erreur: {e}")
