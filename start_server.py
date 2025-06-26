#!/usr/bin/env python3
"""
Script de démarrage du serveur FastAPI
"""
import subprocess
import sys
import os
import time

def start_server():
    """Démarre le serveur FastAPI"""
    print("Démarrage du serveur OSINT-AI...")
    
    # Changer vers le répertoire du projet
    os.chdir('/workspaces/abdou.github.io')
    
    # Supprimer la variable DATABASE_URL pour forcer SQLite
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    try:
        # Démarrer uvicorn
        cmd = [
            sys.executable, '-m', 'uvicorn', 
            'backend.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000',
            '--reload'
        ]
        
        print(f"Commande: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        print("Serveur démarré avec succès!")
        print("Accédez à http://localhost:8000 pour l'API")
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Attendre que le processus se termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        process.terminate()
    except Exception as e:
        print(f"Erreur lors du démarrage: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server()
