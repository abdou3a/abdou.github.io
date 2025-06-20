#!/usr/bin/env python3
"""
Point d'entrée WSGI pour le serveur C2
"""

import os
from c2_server import app

if __name__ == '__main__':
    # Configuration pour la production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    # Configuration de sécurité
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    
    # Configuration de la base de données
    app.config['DATABASE_PATH'] = os.environ.get('DATABASE_PATH', '/var/www/c2-server/c2_server.db')
    
    # Lancement du serveur
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(host=host, port=port, debug=False)b