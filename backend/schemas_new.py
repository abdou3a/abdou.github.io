from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    subscription_tier: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    subscription_tier: str
    searches_used_today: int
    subscription_end_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# OSINT Search Schemas
class OSINTSearchCreate(BaseModel):
    target: str
    search_type: str  # person, handle, domain, email, etc.

class OSINTSearchResponse(BaseModel):
    id: int
    target: str
    search_type: str
    status: str
    confidence_score: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionPlan(BaseModel):
    name: str
    price: float
    searches_per_day: int
    features: List[str]
    stripe_price_id: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SearchLimits(BaseModel):
    searches_used_today: int
    searches_remaining: int
    subscription_tier: str
    reset_time: datetime
