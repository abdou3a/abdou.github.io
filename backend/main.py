from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import jwt
import bcrypt
import stripe
import os
import asyncio
import json
from contextlib import asynccontextmanager

from backend.database import SessionLocal, engine, get_db
from backend.models import Base, User, Search, Payment, SubscriptionPlan, SearchStatus
from backend.schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    SearchCreate, SearchResponse, 
    DashboardStats, TokenResponse, APIResponse,
    PricingPlan, ContactMessage, SubscriptionCreate
)
from backend.auth import create_access_token, verify_token, get_current_user, hash_password
from backend.osint_engine import OSINTEngine
from backend.rate_limiter import RateLimiter

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Stripe configuration
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Pricing configuration
PRICING_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "searches_per_month": 3,
        "features": [
            "3 recherches par mois",
            "Rapports basiques",
            "Support communautaire"
        ],
        "stripe_price_id": None
    },
    "premium": {
        "name": "Premium", 
        "price": 29.99,
        "searches_per_month": 100,
        "features": [
            "100 recherches par mois",
            "Rapports détaillés avec IA",
            "Export PDF/JSON",
            "Support prioritaire",
            "API access"
        ],
        "stripe_price_id": os.getenv("STRIPE_PREMIUM_PRICE_ID")
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "searches_per_month": 1000,
        "features": [
            "1000 recherches par mois",
            "Rapports avancés",
            "Intégrations personnalisées",
            "Support dédié 24/7",
            "API illimitée",
            "Formation équipe"
        ],
        "stripe_price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID")
    }
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("🚀 OSINT-AI Platform démarrée")
    yield
    # Shutdown
    print("⏹️ OSINT-AI Platform arrêtée")

# Initialize FastAPI app
app = FastAPI(
    title="OSINT-AI Platform",
    description="Plateforme d'intelligence artificielle pour l'investigation OSINT",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
rate_limiter = RateLimiter()

# Initialize OSINT Engine
osint_engine = OSINTEngine()

# Static files (for serving the landing page)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/api/auth/register", response_model=APIResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(User.email == user_data.email, User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ou nom d'utilisateur déjà utilisé"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            subscription_plan=SubscriptionPlan.FREE,
            searches_limit=PRICING_PLANS["free"]["searches_per_month"]
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return APIResponse(
            success=True,
            message="Compte créé avec succès",
            data={"user_id": new_user.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user or not bcrypt.checkpw(
            credentials.password.encode('utf-8'), 
            user.hashed_password.encode('utf-8')
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Compte désactivé"
            )
        
        access_token = create_access_token(data={"sub": user.email})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de connexion: {str(e)}"
        )

# ========== USER MANAGEMENT ==========

@app.get("/api/user/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Récupérer le profil utilisateur"""
    return UserResponse.from_orm(current_user)

@app.put("/api/user/profile", response_model=APIResponse)
async def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour le profil utilisateur"""
    try:
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return APIResponse(
            success=True,
            message="Profil mis à jour avec succès"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@app.get("/api/user/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les statistiques du dashboard"""
    try:
        # Get user's searches
        searches = db.query(Search).filter(Search.user_id == current_user.id).all()
        recent_searches = db.query(Search).filter(
            Search.user_id == current_user.id
        ).order_by(Search.created_at.desc()).limit(5).all()
        
        # Check subscription status
        subscription_active = (
            current_user.subscription_end_date is None or 
            current_user.subscription_end_date > datetime.utcnow()
        ) if current_user.subscription_plan != SubscriptionPlan.FREE else True
        
        return DashboardStats(
            total_searches=len(searches),
            searches_used=current_user.searches_used,
            searches_remaining=max(0, current_user.searches_limit - current_user.searches_used),
            subscription_plan=current_user.subscription_plan,
            subscription_active=subscription_active,
            recent_searches=[SearchResponse.from_orm(s) for s in recent_searches]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du chargement du dashboard: {str(e)}"
        )

# ========== OSINT SEARCH ENDPOINTS ==========

@app.post("/api/search", response_model=SearchResponse)
async def create_search(
    search_data: SearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer une nouvelle recherche OSINT"""
    try:
        # Check user limits
        if current_user.searches_used >= current_user.searches_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Limite de recherches atteinte. Veuillez upgrader votre abonnement."
            )
        
        # Rate limiting
        await rate_limiter.check_rate_limit(current_user.id)
        
        # Create search record
        search = Search(
            user_id=current_user.id,
            target=search_data.target,
            search_type=search_data.search_type.value,
            status=SearchStatus.PENDING
        )
        
        db.add(search)
        db.commit()
        db.refresh(search)
        
        # Start OSINT search asynchronously
        asyncio.create_task(process_osint_search(search.id))
        
        # Update user search count
        current_user.searches_used += 1
        db.commit()
        
        return SearchResponse.from_orm(search)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la recherche: {str(e)}"
        )

@app.get("/api/search/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer une recherche spécifique"""
    search = db.query(Search).filter(
        and_(Search.id == search_id, Search.user_id == current_user.id)
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recherche non trouvée"
        )
    
    return SearchResponse.from_orm(search)

@app.get("/api/search", response_model=List[SearchResponse])
async def get_user_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Récupérer toutes les recherches de l'utilisateur"""
    searches = db.query(Search).filter(
        Search.user_id == current_user.id
    ).order_by(Search.created_at.desc()).offset(skip).limit(limit).all()
    
    return [SearchResponse.from_orm(search) for search in searches]

# ========== SUBSCRIPTION & BILLING ==========

@app.get("/api/pricing", response_model=List[PricingPlan])
async def get_pricing():
    """Récupérer les plans tarifaires"""
    plans = []
    for plan_id, plan_data in PRICING_PLANS.items():
        plans.append(PricingPlan(
            name=plan_data["name"],
            price=plan_data["price"],
            currency="EUR",
            searches_per_month=plan_data["searches_per_month"],
            features=plan_data["features"],
            stripe_price_id=plan_data.get("stripe_price_id", "")
        ))
    return plans

@app.post("/api/subscription/create-checkout", response_model=APIResponse)
async def create_checkout_session(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user)
):
    """Créer une session de paiement Stripe"""
    try:
        if not STRIPE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe non configuré"
            )
        
        plan_data = PRICING_PLANS.get(subscription.plan.value)
        if not plan_data or not plan_data.get("stripe_price_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan non valide"
            )
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': plan_data["stripe_price_id"],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{FRONTEND_URL}/dashboard?success=true",
            cancel_url=f"{FRONTEND_URL}/pricing?cancelled=true",
            metadata={
                'user_id': current_user.id,
                'plan': subscription.plan.value
            }
        )
        
        return APIResponse(
            success=True,
            message="Session créée",
            data={"checkout_url": checkout_session.url}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la session: {str(e)}"
        )

# ========== LANDING PAGE ==========

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Page d'accueil de la plateforme"""
    return await get_landing_page_html()

# ========== HELPER FUNCTIONS ==========

async def process_osint_search(search_id: int):
    """Traiter une recherche OSINT en arrière-plan"""
    db = SessionLocal()
    try:
        search = db.query(Search).filter(Search.id == search_id).first()
        if not search:
            return
        
        # Update status
        search.status = SearchStatus.PROCESSING
        db.commit()
        
        # Perform OSINT search
        results = await osint_engine.search(search.target, search.search_type)
        
        # Update search with results
        search.results = results
        search.confidence_score = results.get("confidence_score", 0.0)
        search.status = SearchStatus.COMPLETED
        search.completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # Update search with error
        search.status = SearchStatus.FAILED
        search.error_message = str(e)
        db.commit()
        
    finally:
        db.close()

async def get_landing_page_html():
    """Génère la page d'accueil HTML avec authentification"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OSINT-AI Platform | Intelligence & Investigation SaaS</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .cyber-grid {
                background-image: radial-gradient(circle at 1px 1px, rgba(34, 197, 94, 0.3) 1px, transparent 0);
                background-size: 20px 20px;
            }
            .glass-effect {
                backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        </style>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white cyber-grid">
        <!-- Navigation -->
        <nav class="bg-black/70 backdrop-blur-sm border-b border-green-500/30">
            <div class="container mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <i class="fas fa-eye text-green-400 text-2xl"></i>
                        <h1 class="text-xl font-bold text-green-400">OSINT-AI Platform</h1>
                    </div>
                    <div class="space-x-4">
                        <button onclick="showLoginModal()" class="bg-green-600 hover:bg-green-500 px-6 py-2 rounded-lg font-semibold transition-colors">
                            Se connecter
                        </button>
                        <button onclick="showRegisterModal()" class="border border-green-500 hover:bg-green-500/20 px-6 py-2 rounded-lg font-semibold transition-colors">
                            S'inscrire
                        </button>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="py-20">
            <div class="container mx-auto px-6 text-center">
                <h2 class="text-5xl font-bold mb-6 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                    OSINT-AI Platform
                </h2>
                <p class="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
                    Plateforme SaaS d'intelligence artificielle pour l'investigation OSINT. 
                    Recherchez, analysez et obtenez des insights professionnels.
                </p>
                <button onclick="showRegisterModal()" class="bg-green-600 hover:bg-green-500 text-white px-8 py-4 rounded-lg text-lg font-bold transition-all transform hover:scale-105">
                    Commencer gratuitement
                </button>
            </div>
        </section>

        <!-- Features -->
        <section class="py-20">
            <div class="container mx-auto px-6">
                <h3 class="text-3xl font-bold text-center mb-12">Fonctionnalités</h3>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="glass-effect rounded-lg p-6 text-center">
                        <i class="fas fa-search text-green-400 text-4xl mb-4"></i>
                        <h4 class="text-xl font-bold mb-2">Recherche OSINT</h4>
                        <p class="text-gray-300">Analyse complète de personnes, handles, domaines</p>
                    </div>
                    <div class="glass-effect rounded-lg p-6 text-center">
                        <i class="fas fa-brain text-blue-400 text-4xl mb-4"></i>
                        <h4 class="text-xl font-bold mb-2">IA Avancée</h4>
                        <p class="text-gray-300">Scoring de confiance et analyse intelligente</p>
                    </div>
                    <div class="glass-effect rounded-lg p-6 text-center">
                        <i class="fas fa-chart-line text-purple-400 text-4xl mb-4"></i>
                        <h4 class="text-xl font-bold mb-2">Rapports Détaillés</h4>
                        <p class="text-gray-300">Visualisations et exports professionnels</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Pricing -->
        <section class="py-20">
            <div class="container mx-auto px-6">
                <h3 class="text-3xl font-bold text-center mb-12">Plans & Tarifs</h3>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="glass-effect rounded-lg p-8 text-center">
                        <h4 class="text-2xl font-bold mb-4">Free</h4>
                        <div class="text-4xl font-bold mb-6">0€<span class="text-lg">/mois</span></div>
                        <ul class="space-y-2 mb-8">
                            <li><i class="fas fa-check text-green-400 mr-2"></i>3 recherches/mois</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Rapports basiques</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Support communautaire</li>
                        </ul>
                        <button onclick="showRegisterModal()" class="w-full bg-gray-600 hover:bg-gray-500 py-3 rounded-lg font-semibold">
                            Commencer
                        </button>
                    </div>
                    <div class="glass-effect rounded-lg p-8 text-center border-2 border-green-500 relative">
                        <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-black px-4 py-1 rounded-full text-sm font-bold">
                            Populaire
                        </div>
                        <h4 class="text-2xl font-bold mb-4">Premium</h4>
                        <div class="text-4xl font-bold mb-6">29€<span class="text-lg">/mois</span></div>
                        <ul class="space-y-2 mb-8">
                            <li><i class="fas fa-check text-green-400 mr-2"></i>100 recherches/mois</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Rapports IA détaillés</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Export PDF/JSON</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Support prioritaire</li>
                        </ul>
                        <button onclick="showRegisterModal()" class="w-full bg-green-600 hover:bg-green-500 py-3 rounded-lg font-semibold">
                            Choisir Premium
                        </button>
                    </div>
                    <div class="glass-effect rounded-lg p-8 text-center">
                        <h4 class="text-2xl font-bold mb-4">Enterprise</h4>
                        <div class="text-4xl font-bold mb-6">99€<span class="text-lg">/mois</span></div>
                        <ul class="space-y-2 mb-8">
                            <li><i class="fas fa-check text-green-400 mr-2"></i>1000 recherches/mois</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Rapports avancés</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>API illimitée</li>
                            <li><i class="fas fa-check text-green-400 mr-2"></i>Support 24/7</li>
                        </ul>
                        <button onclick="showRegisterModal()" class="w-full bg-purple-600 hover:bg-purple-500 py-3 rounded-lg font-semibold">
                            Contacter
                        </button>
                    </div>
                </div>
            </div>
        </section>

        <!-- Login Modal -->
        <div id="loginModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden z-50">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="glass-effect rounded-lg p-8 max-w-md w-full">
                    <h3 class="text-2xl font-bold mb-6 text-center">Connexion</h3>
                    <form id="loginForm">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Email</label>
                            <input type="email" id="loginEmail" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Mot de passe</label>
                            <input type="password" id="loginPassword" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white py-3 rounded-lg font-semibold transition-colors">
                            Se connecter
                        </button>
                    </form>
                    <button onclick="closeModals()" class="absolute top-4 right-4 text-gray-400 hover:text-white">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Register Modal -->
        <div id="registerModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden z-50">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="glass-effect rounded-lg p-8 max-w-md w-full">
                    <h3 class="text-2xl font-bold mb-6 text-center">Inscription</h3>
                    <form id="registerForm">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Nom complet</label>
                            <input type="text" id="registerName" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Nom d'utilisateur</label>
                            <input type="text" id="registerUsername" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Email</label>
                            <input type="email" id="registerEmail" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Mot de passe</label>
                            <input type="password" id="registerPassword" required class="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 focus:border-green-400 focus:outline-none">
                        </div>
                        <button type="submit" class="w-full bg-green-600 hover:bg-green-500 text-white py-3 rounded-lg font-semibold transition-colors">
                            S'inscrire
                        </button>
                    </form>
                    <button onclick="closeModals()" class="absolute top-4 right-4 text-gray-400 hover:text-white">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>

        <script>
            function showLoginModal() {
                document.getElementById('loginModal').classList.remove('hidden');
            }
            
            function showRegisterModal() {
                document.getElementById('registerModal').classList.remove('hidden');
            }
            
            function closeModals() {
                document.getElementById('loginModal').classList.add('hidden');
                document.getElementById('registerModal').classList.add('hidden');
            }

            // Login form handler
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('loginEmail').value;
                const password = document.getElementById('loginPassword').value;
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        localStorage.setItem('token', data.access_token);
                        alert('Connexion réussie! Redirection vers le dashboard...');
                        setTimeout(() => {
                            window.location.href = '/frontend/src/pages/dashboard.html';
                        }, 1000);
                    } else {
                        alert(data.detail || 'Erreur de connexion');
                    }
                } catch (error) {
                    alert('Erreur de connexion');
                }
            });

            // Register form handler
            document.getElementById('registerForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const full_name = document.getElementById('registerName').value;
                const username = document.getElementById('registerUsername').value;
                const email = document.getElementById('registerEmail').value;
                const password = document.getElementById('registerPassword').value;
                
                try {
                    const response = await fetch('/api/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ full_name, username, email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Compte créé avec succès! Veuillez vous connecter.');
                        closeModals();
                        showLoginModal();
                    } else {
                        alert(data.detail || 'Erreur lors de la création du compte');
                    }
                } catch (error) {
                    alert('Erreur lors de la création du compte');
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
