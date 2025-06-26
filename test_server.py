import sys
sys.path.append('/workspaces/abdou.github.io')

try:
    from backend.main import app
    print("✅ Import de l'application FastAPI réussi")
    
    # Test des endpoints principaux
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test endpoint de santé
    response = client.get("/health")
    print(f"✅ Endpoint /health: {response.status_code}")
    
    print("🚀 Le serveur semble prêt à fonctionner!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
