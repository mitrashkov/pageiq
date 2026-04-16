"""
Stripe Payment Integration Service for PageIQ
Handles subscriptions, billing, and payment processing.
"""
import logging
import os
from typing import Optional, Dict, Any

import stripe
from sqlalchemy.orm import Session

from app.models import User

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY", "")


class StripeService:
    """Service for handling Stripe payments and subscriptions."""
    
    # Product IDs from Stripe
    PRODUCTS = {
        "free": os.getenv("STRIPE_PRODUCT_FREE", "prod_free"),
        "starter": os.getenv("STRIPE_PRODUCT_STARTER", "prod_starter"),
        "pro": os.getenv("STRIPE_PRODUCT_PRO", "prod_pro"),
        "business": os.getenv("STRIPE_PRODUCT_BUSINESS", "prod_business"),
        "enterprise": os.getenv("STRIPE_PRODUCT_ENTERPRISE", "prod_enterprise"),
    }
    
    # Pricing for each tier
    PRICING = {
        "free": {"monthly": 0, "yearly": 0, "quota": 100},
        "starter": {"monthly": 9, "yearly": 96, "quota": 5000},
        "pro": {"monthly": 29, "yearly": 319, "quota": 50000},
        "business": {"monthly": 99, "yearly": 1090, "quota": 500000},
        "enterprise": {"monthly": None, "yearly": None, "quota": None},
    }
    
    @staticmethod
    def create_customer(user: User, db: Session) -> Optional[str]:
        """
        Create a Stripe customer for a user.
        
        Args:
            user: User object
            db: Database session
            
        Returns:
            Stripe customer ID
        """
        try:
            # Check if customer already exists
            if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
                return user.stripe_customer_id
            
            # Create new customer
            customer = stripe.Customer.create(
                email=user.email,
                name=f"User {user.id}",
                metadata={
                    "user_id": str(user.id),
                    "created_at": str(user.created_at) if hasattr(user, 'created_at') else None
                }
            )
            
            # Store customer ID on user
            user.stripe_customer_id = customer.id
            db.commit()
            
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            return None
    
    @staticmethod
    def create_subscription(
        user: User,
        plan: str,
        db: Session,
        billing_cycle: str = "monthly"
    ) -> Optional[str]:
        """
        Create a subscription for a user.
        
        Args:
            user: User object
            plan: Plan name (free, starter, pro, business, enterprise)
            db: Database session
            billing_cycle: "monthly" or "yearly"
            
        Returns:
            Stripe subscription ID
        """
        try:
            # Get or create Stripe customer
            customer_id = StripeService.create_customer(user, db)
            if not customer_id:
                raise ValueError("Could not create Stripe customer")
            
            # Get product ID
            product_id = StripeService.PRODUCTS.get(plan)
            if not product_id:
                raise ValueError(f"Unknown plan: {plan}")
            
            # Free tier doesn't need subscription
            if plan == "free":
                logger.info(f"Free tier for user {user.id}")
                return None
            
            # Get price ID based on billing cycle
            prices = stripe.Price.list(product=product_id)
            price_id = None
            
            for price in prices.data:
                if billing_cycle == "monthly" and price.recurring.interval == "month":
                    price_id = price.id
                    break
                elif billing_cycle == "yearly" and price.recurring.interval == "year":
                    price_id = price.id
                    break
            
            if not price_id:
                raise ValueError(f"No price found for {plan} {billing_cycle}")
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={
                    "user_id": str(user.id),
                    "plan": plan,
                    "billing_cycle": billing_cycle
                }
            )
            
            logger.info(f"Created Stripe subscription {subscription.id} for user {user.id}")
            return subscription.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            True if successful
        """
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"Canceled subscription {subscription_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {str(e)}")
            return False
    
    @staticmethod
    def upgrade_subscription(
        user: User,
        new_plan: str,
        db: Session
    ) -> bool:
        """
        Upgrade user to a new plan.
        
        Args:
            user: User object
            new_plan: New plan name
            db: Database session
            
        Returns:
            True if successful
        """
        try:
            # Get current subscription
            if not hasattr(user, 'stripe_subscription_id') or not user.stripe_subscription_id:
                # Create new subscription
                StripeService.create_subscription(user, new_plan, db)
                return True
            
            # Get new price
            product_id = StripeService.PRODUCTS.get(new_plan)
            prices = stripe.Price.list(product=product_id)
            
            if not prices.data:
                raise ValueError(f"No prices for {new_plan}")
            
            price_id = prices.data[0].id
            
            # Update subscription
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                items=[{
                    "id": stripe.Subscription.retrieve(user.stripe_subscription_id).items.data[0].id,
                    "price": price_id
                }],
                metadata={"plan": new_plan}
            )
            
            logger.info(f"Upgraded user {user.id} to {new_plan}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Error upgrading subscription: {str(e)}")
            return False
    
    @staticmethod
    def get_subscription_details(subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details from Stripe.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription details dictionary
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "plan": subscription.metadata.get("plan"),
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "items": [
                    {
                        "id": item.id,
                        "price": item.price.id,
                        "amount": item.price.unit_amount / 100,  # Convert to dollars
                        "currency": item.price.currency,
                        "interval": item.price.recurring.interval if item.price.recurring else None
                    }
                    for item in subscription.items.data
                ]
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error getting subscription details: {str(e)}")
            return None
    
    @staticmethod
    def process_webhook(event: Dict[str, Any]) -> bool:
        """
        Process Stripe webhook event.
        
        Args:
            event: Stripe webhook event
            
        Returns:
            True if processed successfully
        """
        try:
            event_type = event.get("type")
            
            if event_type == "payment_intent.succeeded":
                logger.info("Payment succeeded")
                # TODO: Update user quota/subscription
                
            elif event_type == "invoice.payment_succeeded":
                logger.info("Invoice payment succeeded")
                # TODO: Log payment
                
            elif event_type == "invoice.payment_failed":
                logger.error("Invoice payment failed")
                # TODO: Notify user, disable API key
                
            elif event_type == "customer.subscription.created":
                logger.info("Subscription created")
                # TODO: Enable features for new plan
                
            elif event_type == "customer.subscription.updated":
                logger.info("Subscription updated")
                # TODO: Update user permissions
                
            elif event_type == "customer.subscription.deleted":
                logger.info("Subscription deleted")
                # TODO: Downgrade to free tier
                
            else:
                logger.warning(f"Unhandled webhook type: {event_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return False
    
    @staticmethod
    def get_invoices(customer_id: str, limit: int = 10) -> list:
        """
        Get invoices for a customer.
        
        Args:
            customer_id: Stripe customer ID
            limit: Number of invoices to fetch
            
        Returns:
            List of invoice details
        """
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
            
            return [
                {
                    "id": invoice.id,
                    "date": invoice.created,
                    "amount": invoice.total / 100,  # Convert to dollars
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "pdf_url": invoice.invoice_pdf
                }
                for invoice in invoices.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Error getting invoices: {str(e)}")
            return []
    
    @staticmethod
    def get_payment_methods(customer_id: str) -> list:
        """
        Get payment methods for a customer.
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            List of payment method details
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [
                {
                    "id": pm.id,
                    "card_last4": pm.card.last4,
                    "card_brand": pm.card.brand,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year
                }
                for pm in payment_methods.data
            ]
        except stripe.error.StripeError as e:
            logger.error(f"Error getting payment methods: {str(e)}")
            return []
    
    @staticmethod
    def add_payment_method(customer_id: str, payment_method_id: str) -> bool:
        """
        Add a payment method to a customer.
        
        Args:
            customer_id: Stripe customer ID
            payment_method_id: Payment method ID from Stripe
            
        Returns:
            True if successful
        """
        try:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )
            
            logger.info(f"Added payment method for customer {customer_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error adding payment method: {str(e)}")
            return False


# Global instance
stripe_service = StripeService()
