from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionPlan(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SearchType(str, Enum):
    PERSON = "person"
    HANDLE = "handle"
    EMAIL = "email"
    DOMAIN = "domain"
    PHONE = "phone"
    CUSTOM = "custom"

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

class UserResponse(UserBase):
    id: int
    role: str
    subscription_plan: str
    is_active: bool
    email_verified: bool
    searches_used: int
    searches_limit: int
    subscription_end_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
# Search Schemas
class SearchCreate(BaseModel):
    target: str = Field(..., min_length=1, max_length=500)
    search_type: SearchType

class SearchResponse(BaseModel):
    id: int
    target: str
    search_type: str
    status: str
    confidence_score: Optional[float] = None
    report_url: Optional[str] = None
    cost_credits: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan

class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    plan_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_searches: int
    searches_used: int
    searches_remaining: int
    subscription_plan: str
    subscription_active: bool
    recent_searches: List[SearchResponse]

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Pricing Plans
class PricingPlan(BaseModel):
    name: str
    price: float
    currency: str
    searches_per_month: int
    features: List[str]
    stripe_price_id: str

# Contact/Support
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
