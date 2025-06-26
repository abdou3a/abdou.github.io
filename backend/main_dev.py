"""
Version simplifiée du serveur OSINT-AI pour développement
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import os

# Import des modules backend
from backend.database import get_db, engine
from backend.models import Base, User, Search, SubscriptionPlan

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser FastAPI
app = FastAPI(title="OSINT-AI Development Server", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Modèles Pydantic
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    plan: str = "free"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Fonctions utilitaires
def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoints
@app.get("/")
async def root():
    return {"message": "OSINT-AI Development Server is running!", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "OSINT-AI", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Un utilisateur avec cet email ou nom d'utilisateur existe déjà"
            )
        
        # Créer le nouvel utilisateur
        hashed_password = hash_password(user_data.password)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            plan=user_data.plan,
            searches_this_month=0,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Créer le token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(db_user)
        }
        
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'inscription: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du compte")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    try:
        # Trouver l'utilisateur
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Email ou mot de passe incorrect"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Compte désactivé"
            )
        
        # Créer le token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur lors de la connexion: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(db: Session = Depends(get_db)):
    """Récupérer les informations de l'utilisateur actuel"""
    # Pour le développement, on retourne un utilisateur de test
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "plan": "free",
        "created_at": datetime.utcnow()
    }

@app.get("/api/pricing")
async def get_pricing():
    """Récupérer les plans de tarification"""
    return {
        "plans": {
            "free": {
                "name": "Free",
                "price": 0,
                "searches_per_month": 3,
                "features": ["3 recherches par mois", "Rapports basiques"]
            },
            "premium": {
                "name": "Premium",
                "price": 19.99,
                "searches_per_month": 100,
                "features": ["100 recherches par mois", "Rapports avancés"]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99.99,
                "searches_per_month": 1000,
                "features": ["1000 recherches par mois", "Support prioritaire"]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
