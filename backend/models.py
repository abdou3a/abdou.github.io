from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SearchStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER)
    subscription_plan = Column(String, default=SubscriptionPlan.FREE)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    searches_used = Column(Integer, default=0)
    searches_limit = Column(Integer, default=3)  # Free plan limit
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    searches_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    searches = relationship("Search", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

class Search(Base):
    __tablename__ = "searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    target = Column(String, nullable=False)
    search_type = Column(String, nullable=False)
    results = Column(JSON)
    confidence_score = Column(Float)
    status = Column(String, default=SearchStatus.PENDING)
    report_url = Column(String, nullable=True)
    cost_credits = Column(Integer, default=1)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="searches")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    stripe_payment_id = Column(String, unique=True)
    amount = Column(Float)
    currency = Column(String, default="eur")
    plan_type = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    key_hash = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    requests_made = Column(Integer, default=0)
    requests_limit = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class Investigation(Base):
    __tablename__ = "investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, completed, archived
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="investigations")
    search_queries = relationship("SearchQuery", back_populates="investigation")

class SearchQuery(Base):
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=True)
    query_type = Column(String, nullable=False)  # person, email, domain, phone, etc.
    query_data = Column(JSON, nullable=False)  # Original search parameters
    status = Column(String, default="pending")  # pending, processing, completed, failed
    results = Column(JSON, nullable=True)  # Search results
    error_message = Column(Text, nullable=True)
    sources_used = Column(JSON, nullable=True)  # List of sources used
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="search_queries")
    investigation = relationship("Investigation", back_populates="search_queries")

class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    query_id = Column(Integer, ForeignKey("search_queries.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_usage")

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # social_media, public_records, news, etc.
    is_active = Column(Boolean, default=True)
    requires_api_key = Column(Boolean, default=False)
    rate_limit_per_hour = Column(Integer, default=100)
    confidence_score = Column(Integer, default=80)  # Reliability score 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False)
    source_name = Column(String, nullable=False)
    result_type = Column(String, nullable=False)  # profile, post, document, etc.
    data = Column(JSON, nullable=False)  # The actual result data
    confidence_score = Column(Integer, default=50)  # AI confidence 0-100
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    search_query = relationship("SearchQuery")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("search_queries.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # sentiment, face_recognition, etc.
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    search_query = relationship("SearchQuery")

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of events to listen for
    is_active = Column(Boolean, default=True)
    secret = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class OSINTSearch(Base):
    __tablename__ = "osint_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target = Column(String, nullable=False)
    search_type = Column(String, nullable=False)  # person, handle, domain, etc.
    results = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="osint_searches")
