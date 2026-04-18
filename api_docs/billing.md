# /account

**Methods:** GET, POST

**Description:**
Subscription and billing management endpoints for authenticated users.

**Endpoints:**
- `/account/subscription` (GET): Get current subscription status and plan details.
- `/account/subscription/upgrade` (POST): Upgrade or change plan.
- `/account/subscription/cancel` (POST): Cancel active subscription and downgrade.
- `/account/billing/invoices` (GET): List billing invoices.
- `/account/billing/payment-methods` (GET): List saved payment methods.
- `/account/billing/payment-methods` (POST): Attach a payment method.
- `/account/webhooks/stripe` (POST): Stripe webhook receiver.
- `/account/account/billing-summary` (GET): Billing and quota summary.

**Authentication:**
- Requires authenticated user context on all account endpoints.
