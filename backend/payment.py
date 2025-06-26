import stripe
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class StripePayment:
    """Stripe payment processing service"""
    
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # Subscription plans with Stripe Price IDs
        self.plans = {
            "starter": {
                "price_id": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter_monthly"),
                "name": "Starter Plan",
                "amount": 2900,  # $29.00 in cents
                "currency": "usd",
                "interval": "month",
                "features": ["100 searches/month", "Basic reports", "Email support"]
            },
            "professional": {
                "price_id": os.getenv("STRIPE_PROFESSIONAL_PRICE_ID", "price_professional_monthly"),
                "name": "Professional Plan",
                "amount": 9900,  # $99.00 in cents
                "currency": "usd",
                "interval": "month",
                "features": ["1,000 searches/month", "AI analysis", "Priority support", "API access"]
            },
            "enterprise": {
                "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise_monthly"),
                "name": "Enterprise Plan",
                "amount": 29900,  # $299.00 in cents
                "currency": "usd",
                "interval": "month",
                "features": ["Unlimited searches", "White-label", "Custom integrations", "24/7 support"]
            }
        }
    
    def create_customer(self, email: str, name: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new Stripe customer"""
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "created": datetime.fromtimestamp(customer.created)
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    def create_subscription(self, customer_email: str, plan: str, payment_method_id: str = None) -> Dict[str, Any]:
        """Create a new subscription"""
        
        if plan not in self.plans:
            raise ValueError(f"Invalid plan: {plan}")
        
        try:
            # Create or get customer
            customers = stripe.Customer.list(email=customer_email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(email=customer_email)
            
            # Create subscription
            subscription_params = {
                "customer": customer.id,
                "items": [{"price": self.plans[plan]["price_id"]}],
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "plan": plan,
                    "created_by": "osint_ai_platform"
                }
            }
            
            if payment_method_id:
                subscription_params["default_payment_method"] = payment_method_id
            
            subscription = stripe.Subscription.create(**subscription_params)
            
            return {
                "subscription_id": subscription.id,
                "customer_id": customer.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "plan": plan,
                "amount": self.plans[plan]["amount"]
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel a subscription"""
        
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def change_subscription_plan(self, subscription_id: str, new_plan: str) -> Dict[str, Any]:
        """Change subscription plan"""
        
        if new_plan not in self.plans:
            raise ValueError(f"Invalid plan: {new_plan}")
        
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": self.plans[new_plan]["price_id"]
                }],
                metadata={
                    **subscription.metadata,
                    "plan": new_plan,
                    "plan_changed_at": str(datetime.utcnow())
                }
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "new_plan": new_plan,
                "amount": self.plans[new_plan]["amount"],
                "effective_date": datetime.fromtimestamp(updated_subscription.current_period_start)
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to change subscription plan: {str(e)}")
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
                "metadata": subscription.metadata
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get subscription: {str(e)}")
    
    def create_payment_intent(self, amount: int, currency: str = "usd", customer_id: str = None) -> Dict[str, Any]:
        """Create a payment intent for one-time payments"""
        
        try:
            payment_intent_params = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods": {"enabled": True}
            }
            
            if customer_id:
                payment_intent_params["customer"] = customer_id
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    def create_setup_intent(self, customer_id: str) -> Dict[str, Any]:
        """Create a setup intent for saving payment methods"""
        
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"]
            )
            
            return {
                "setup_intent_id": setup_intent.id,
                "client_secret": setup_intent.client_secret,
                "status": setup_intent.status
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create setup intent: {str(e)}")
    
    def get_customer_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's saved payment methods"""
        
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [{
                "payment_method_id": pm.id,
                "type": pm.type,
                "card": {
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year
                } if pm.card else None,
                "created": datetime.fromtimestamp(pm.created)
            } for pm in payment_methods.data]
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get payment methods: {str(e)}")
    
    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            result = {
                "event_id": event["id"],
                "event_type": event_type,
                "processed": True,
                "data": {}
            }
            
            # Handle different event types
            if event_type == "customer.subscription.created":
                result["data"] = {
                    "subscription_id": event_data["id"],
                    "customer_id": event_data["customer"],
                    "status": event_data["status"],
                    "plan": event_data["metadata"].get("plan", "unknown")
                }
                
            elif event_type == "customer.subscription.updated":
                result["data"] = {
                    "subscription_id": event_data["id"],
                    "customer_id": event_data["customer"],
                    "status": event_data["status"],
                    "cancel_at_period_end": event_data["cancel_at_period_end"]
                }
                
            elif event_type == "customer.subscription.deleted":
                result["data"] = {
                    "subscription_id": event_data["id"],
                    "customer_id": event_data["customer"],
                    "canceled_at": event_data["canceled_at"]
                }
                
            elif event_type == "invoice.payment_succeeded":
                result["data"] = {
                    "invoice_id": event_data["id"],
                    "customer_id": event_data["customer"],
                    "subscription_id": event_data["subscription"],
                    "amount_paid": event_data["amount_paid"],
                    "currency": event_data["currency"]
                }
                
            elif event_type == "invoice.payment_failed":
                result["data"] = {
                    "invoice_id": event_data["id"],
                    "customer_id": event_data["customer"],
                    "subscription_id": event_data["subscription"],
                    "amount_due": event_data["amount_due"],
                    "attempt_count": event_data["attempt_count"]
                }
            
            return result
            
        except ValueError as e:
            raise Exception(f"Invalid webhook payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid webhook signature: {str(e)}")
    
    def get_billing_portal_url(self, customer_id: str, return_url: str) -> str:
        """Create billing portal session for customer"""
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create billing portal: {str(e)}")
    
    def get_usage_based_pricing_data(self, subscription_id: str) -> Dict[str, Any]:
        """Get usage data for metered billing (if implemented)"""
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get usage records for metered items
            usage_data = {}
            
            for item in subscription["items"]["data"]:
                if item["price"]["billing_scheme"] == "per_unit":
                    usage_records = stripe.SubscriptionItem.list_usage_record_summaries(
                        item["id"],
                        limit=12  # Last 12 periods
                    )
                    
                    usage_data[item["price"]["nickname"]] = [
                        {
                            "period_start": record["period"]["start"],
                            "period_end": record["period"]["end"],
                            "total_usage": record["total_usage"]
                        }
                        for record in usage_records["data"]
                    ]
            
            return usage_data
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get usage data: {str(e)}")
    
    def report_usage(self, subscription_item_id: str, quantity: int, timestamp: Optional[int] = None) -> Dict[str, Any]:
        """Report usage for metered billing"""
        
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.utcnow().timestamp()),
                action="increment"
            )
            
            return {
                "usage_record_id": usage_record.id,
                "quantity": usage_record.quantity,
                "timestamp": datetime.fromtimestamp(usage_record.timestamp)
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to report usage: {str(e)}")
