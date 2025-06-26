"""
Serveur FastAPI minimal pour test
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OSINT-AI Test Server")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "OSINT-AI Server is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "OSINT-AI"}

@app.post("/api/auth/register")
async def register(request: dict):
    """Test endpoint pour l'inscription"""
    print(f"Received registration request: {request}")
    return {"message": "Registration successful", "user_id": 123}

@app.post("/api/auth/login")
async def login(request: dict):
    """Test endpoint pour la connexion"""
    print(f"Received login request: {request}")
    return {"message": "Login successful", "token": "test_token_123"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
