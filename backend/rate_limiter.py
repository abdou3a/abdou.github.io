import redis
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class RateLimiter:
    """Rate limiting service using Redis"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )
        
        # Rate limits per subscription plan (per month)
        self.rate_limits = {
            "starter": int(os.getenv("RATE_LIMIT_STARTER", 100)),
            "professional": int(os.getenv("RATE_LIMIT_PROFESSIONAL", 1000)),
            "enterprise": int(os.getenv("RATE_LIMIT_ENTERPRISE", -1))  # Unlimited
        }
    
    def _get_monthly_key(self, user_id: int) -> str:
        """Generate Redis key for monthly usage"""
        current_month = datetime.utcnow().strftime("%Y-%m")
        return f"rate_limit:user:{user_id}:month:{current_month}"
    
    def _get_daily_key(self, user_id: int) -> str:
        """Generate Redis key for daily usage"""
        current_day = datetime.utcnow().strftime("%Y-%m-%d")
        return f"rate_limit:user:{user_id}:day:{current_day}"
    
    def check_limit(self, user_id: int, subscription_plan: str) -> bool:
        """Check if user has exceeded rate limit"""
        
        limit = self.rate_limits.get(subscription_plan, 100)
        
        # Enterprise users have unlimited access
        if limit == -1:
            return True
        
        # Get current usage
        monthly_key = self._get_monthly_key(user_id)
        current_usage = int(self.redis_client.get(monthly_key) or 0)
        
        # Check if limit exceeded
        if current_usage >= limit:
            return False
        
        return True
    
    def increment_usage(self, user_id: int, endpoint: str = None) -> int:
        """Increment usage counter and return new count"""
        
        monthly_key = self._get_monthly_key(user_id)
        daily_key = self._get_daily_key(user_id)
        
        # Increment monthly counter
        monthly_count = self.redis_client.incr(monthly_key)
        
        # Set expiry for monthly key (35 days to be safe)
        if monthly_count == 1:
            self.redis_client.expire(monthly_key, 35 * 24 * 60 * 60)
        
        # Increment daily counter
        daily_count = self.redis_client.incr(daily_key)
        
        # Set expiry for daily key (25 hours to be safe)
        if daily_count == 1:
            self.redis_client.expire(daily_key, 25 * 60 * 60)
        
        # Log endpoint usage if specified
        if endpoint:
            endpoint_key = f"rate_limit:user:{user_id}:endpoint:{endpoint}:month:{datetime.utcnow().strftime('%Y-%m')}"
            self.redis_client.incr(endpoint_key)
            self.redis_client.expire(endpoint_key, 35 * 24 * 60 * 60)
        
        return monthly_count
    
    def get_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get usage statistics for user"""
        
        monthly_key = self._get_monthly_key(user_id)
        daily_key = self._get_daily_key(user_id)
        
        monthly_usage = int(self.redis_client.get(monthly_key) or 0)
        daily_usage = int(self.redis_client.get(daily_key) or 0)
        
        return {
            "monthly_usage": monthly_usage,
            "daily_usage": daily_usage,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_endpoint_stats(self, user_id: int) -> Dict[str, int]:
        """Get endpoint usage statistics"""
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        pattern = f"rate_limit:user:{user_id}:endpoint:*:month:{current_month}"
        
        endpoint_stats = {}
        
        for key in self.redis_client.scan_iter(match=pattern):
            # Extract endpoint name from key
            parts = key.split(":")
            if len(parts) >= 5:
                endpoint = parts[4]
                usage = int(self.redis_client.get(key) or 0)
                endpoint_stats[endpoint] = usage
        
        return endpoint_stats
    
    def reset_user_limits(self, user_id: int):
        """Reset all limits for a user (admin function)"""
        
        # Delete all keys for this user
        patterns = [
            f"rate_limit:user:{user_id}:*"
        ]
        
        for pattern in patterns:
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
    
    def set_custom_limit(self, user_id: int, limit: int, duration_days: int = 30):
        """Set custom rate limit for specific user"""
        
        custom_key = f"rate_limit:custom:user:{user_id}"
        
        custom_data = {
            "limit": limit,
            "expires_at": (datetime.utcnow() + timedelta(days=duration_days)).isoformat()
        }
        
        self.redis_client.setex(
            custom_key,
            duration_days * 24 * 60 * 60,
            json.dumps(custom_data)
        )
    
    def get_custom_limit(self, user_id: int) -> Dict[str, Any]:
        """Get custom rate limit for user"""
        
        custom_key = f"rate_limit:custom:user:{user_id}"
        custom_data = self.redis_client.get(custom_key)
        
        if custom_data:
            return json.loads(custom_data)
        
        return None
    
    def check_burst_limit(self, user_id: int, burst_limit: int = 10, window_minutes: int = 1) -> bool:
        """Check burst rate limiting (requests per minute)"""
        
        current_minute = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
        burst_key = f"rate_limit:burst:user:{user_id}:minute:{current_minute}"
        
        current_burst = int(self.redis_client.get(burst_key) or 0)
        
        if current_burst >= burst_limit:
            return False
        
        # Increment and set expiry
        self.redis_client.incr(burst_key)
        self.redis_client.expire(burst_key, window_minutes * 60)
        
        return True
    
    def get_remaining_quota(self, user_id: int, subscription_plan: str) -> Dict[str, Any]:
        """Get remaining quota for user"""
        
        limit = self.rate_limits.get(subscription_plan, 100)
        
        if limit == -1:  # Unlimited
            return {
                "limit": "unlimited",
                "used": self.get_usage_stats(user_id)["monthly_usage"],
                "remaining": "unlimited",
                "reset_date": None
            }
        
        monthly_usage = self.get_usage_stats(user_id)["monthly_usage"]
        remaining = max(0, limit - monthly_usage)
        
        # Calculate reset date (first day of next month)
        now = datetime.utcnow()
        if now.month == 12:
            reset_date = datetime(now.year + 1, 1, 1)
        else:
            reset_date = datetime(now.year, now.month + 1, 1)
        
        return {
            "limit": limit,
            "used": monthly_usage,
            "remaining": remaining,
            "reset_date": reset_date.isoformat()
        }
    
    def cleanup_expired_keys(self):
        """Cleanup expired rate limit keys (maintenance function)"""
        
        # This would be run as a background task
        # Redis handles expiry automatically, but this can clean up any orphaned keys
        
        patterns = [
            "rate_limit:user:*",
            "rate_limit:burst:*",
            "rate_limit:custom:*"
        ]
        
        cleaned_count = 0
        
        for pattern in patterns:
            for key in self.redis_client.scan_iter(match=pattern):
                # Check if key has expiry set
                ttl = self.redis_client.ttl(key)
                if ttl == -1:  # No expiry set
                    # Set a default expiry based on key type
                    if "burst" in key:
                        self.redis_client.expire(key, 60 * 60)  # 1 hour
                    else:
                        self.redis_client.expire(key, 35 * 24 * 60 * 60)  # 35 days
                    cleaned_count += 1
        
        return cleaned_count
