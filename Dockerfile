FROM python:3.11-slim

# Éviter les interactions lors de l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY c2_server.py .
COPY templates/ templates/
COPY .env.example .env

# Création des répertoires de données et logs
RUN mkdir -p /app/data /app/logs

# Permissions et utilisateur non-root
RUN groupadd -r c2user && useradd -r -g c2user c2user
RUN chown -R c2user:c2user /app
USER c2user

# Exposition du port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Point d'entrée
CMD ["python", "c2_server.py"]
