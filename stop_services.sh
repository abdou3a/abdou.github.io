#!/bin/bash
echo "🛑 Arrêt des services OSINT-AI..."

# Arrêter les processus
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
    echo "✅ Backend arrêté"
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
    echo "✅ Frontend arrêté"
fi

# Arrêter Docker si disponible
if command -v docker &> /dev/null; then
    docker-compose -f docker-compose.dev.yml down
    echo "✅ Services Docker arrêtés"
fi

echo "🎉 Tous les services sont arrêtés"
