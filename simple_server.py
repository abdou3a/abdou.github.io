"""
Serveur OSINT-AI ultra-simplifié pour résoudre le problème de connexion
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="OSINT-AI Simple Server")

# Configuration CORS très permissive pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    plan: str = "free"

class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/")
async def root():
    return {"message": "OSINT-AI Server Running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "OSINT-AI"}

@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Endpoint d'inscription simplifié"""
    print(f"Received registration: {user.email}")
    return {
        "message": "User registered successfully",
        "user_id": 123,
        "access_token": "fake_token_for_dev",
        "token_type": "bearer",
        "user": {
            "id": 123,
            "username": user.username,
            "email": user.email,
            "plan": user.plan
        }
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Endpoint de connexion simplifié"""
    print(f"Received login: {credentials.email}")
    return {
        "message": "Login successful",
        "access_token": "fake_token_for_dev",
        "token_type": "bearer",
        "user": {
            "id": 123,
            "username": "testuser",
            "email": credentials.email,
            "plan": "free"
        }
    }

@app.get("/api/pricing")
async def pricing():
    return {
        "plans": {
            "free": {"name": "Free", "price": 0, "searches_per_month": 3},
            "premium": {"name": "Premium", "price": 19.99, "searches_per_month": 100},
            "enterprise": {"name": "Enterprise", "price": 99.99, "searches_per_month": 1000}
        }
    }

if __name__ == "__main__":
    print("🚀 Starting OSINT-AI Simple Server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
