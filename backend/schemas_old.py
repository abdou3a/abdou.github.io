from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SubscriptionPlan(str, Enum):
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"

class SearchStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    subscription_plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Investigation schemas
class InvestigationBase(BaseModel):
    title: str
    description: Optional[str] = None

class InvestigationCreate(InvestigationBase):
    pass

class InvestigationResponse(InvestigationBase):
    id: int
    status: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

# Search schemas
class OSINTSearchRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = ["all"]
    investigation_id: Optional[int] = None
    advanced_options: Optional[Dict[str, Any]] = {}
    
    @validator('query')
    def validate_query(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Query must be at least 2 characters long')
        return v.strip()

class OSINTSearchResponse(BaseModel):
    query_id: Optional[int]
    status: SearchStatus
    results: Optional[Dict[str, Any]] = None
    sources_used: List[str]
    timestamp: datetime
    error_message: Optional[str] = None

class SearchQueryCreate(BaseModel):
    query_type: str
    query_data: Dict[str, Any]
    investigation_id: Optional[int] = None

class SearchQueryResponse(BaseModel):
    id: int
    query_type: str
    query_data: Dict[str, Any]
    status: str
    results: Optional[Dict[str, Any]]
    sources_used: Optional[List[str]]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Person search specific schemas
class PersonSearchRequest(BaseModel):
    full_name: str
    location: Optional[str] = None
    age_range: Optional[List[int]] = None  # [min_age, max_age]
    social_media_platforms: Optional[List[str]] = ["all"]
    include_relatives: Optional[bool] = False
    include_work_history: Optional[bool] = False

class PersonSearchResult(BaseModel):
    name: str
    age: Optional[int]
    location: Optional[str]
    social_profiles: List[Dict[str, Any]]
    photos: List[str]
    work_history: Optional[List[Dict[str, Any]]]
    relatives: Optional[List[Dict[str, Any]]]
    confidence_score: int

# Email search schemas
class EmailSearchRequest(BaseModel):
    email: str
    check_breaches: Optional[bool] = True
    find_social_profiles: Optional[bool] = True
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class EmailSearchResult(BaseModel):
    email: str
    is_valid: bool
    breaches: List[Dict[str, Any]]
    social_profiles: List[Dict[str, Any]]
    owner_info: Optional[Dict[str, Any]]
    confidence_score: int

# Domain search schemas
class DomainSearchRequest(BaseModel):
    domain: str
    include_subdomains: Optional[bool] = True
    include_whois: Optional[bool] = True
    include_dns: Optional[bool] = True
    
    @validator('domain')
    def validate_domain(cls, v):
        if '.' not in v:
            raise ValueError('Invalid domain format')
        return v.lower()

class DomainSearchResult(BaseModel):
    domain: str
    whois_info: Optional[Dict[str, Any]]
    dns_records: Optional[Dict[str, Any]]
    subdomains: List[str]
    ssl_info: Optional[Dict[str, Any]]
    technologies: List[str]
    confidence_score: int

# AI Analysis schemas
class SentimentAnalysisRequest(BaseModel):
    text: str
    
class SentimentAnalysisResult(BaseModel):
    sentiment: str  # positive, negative, neutral
    confidence: float
    keywords: List[str]
    emotions: Dict[str, float]

class FaceRecognitionRequest(BaseModel):
    image_url: str
    compare_with: Optional[List[str]] = []  # URLs of images to compare

class FaceRecognitionResult(BaseModel):
    faces_detected: int
    face_data: List[Dict[str, Any]]
    matches: List[Dict[str, Any]]
    confidence_score: int

# Analytics schemas
class UsageAnalytics(BaseModel):
    current_usage: int
    limit: int
    remaining: int
    reset_date: datetime
    subscription_plan: str

class SearchAnalytics(BaseModel):
    total_searches: int
    searches_by_type: Dict[str, int]
    searches_by_month: Dict[str, int]
    average_confidence: float
    most_used_sources: List[Dict[str, Any]]

# Billing schemas
class SubscriptionCreate(BaseModel):
    plan: SubscriptionPlan
    payment_method_id: str

class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    plan: str

# Webhook schemas
class WebhookCreate(BaseModel):
    url: str
    events: List[str]
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class WebhookResponse(BaseModel):
    id: int
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Error schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime

# Batch operation schemas
class BatchSearchRequest(BaseModel):
    queries: List[OSINTSearchRequest]
    batch_name: Optional[str] = None
    
    @validator('queries')
    def validate_queries(cls, v):
        if len(v) > 100:  # Limit batch size
            raise ValueError('Batch size cannot exceed 100 queries')
        return v

class BatchSearchResponse(BaseModel):
    batch_id: str
    status: str
    total_queries: int
    completed_queries: int
    failed_queries: int
    results: List[OSINTSearchResponse]
