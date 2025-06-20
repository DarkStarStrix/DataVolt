"""
Payment.py: Plan enforcement and payment logic (Stripe integration).
"""
import os
import stripe
from .Config import PLAN_LIMITS, PLAN_PRICING

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Set your Stripe secret key in your environment

class PaymentManager:
    def __init__(self):
        self.stripe_api_key = os.getenv("STRIPE_API_KEY")

    def check_plan_limit(self, plan, requested_tokens):
        limit = PLAN_LIMITS.get(plan, 0)
        return requested_tokens <= limit

    def get_price(self, plan):
        return PLAN_PRICING.get(plan, 0)

    def requires_payment(self, plan, requested_tokens):
        if plan == "free":
            return requested_tokens > PLAN_LIMITS["free"]
        return plan not in PLAN_LIMITS

    def create_checkout_session(self, plan: str, job_id: str, num_tokens: int = 0) -> str:
        amount = int(self.get_price(plan) * 100)  # amount in cents
        if plan == "payg":
            amount = int(self.calculate_token_cost(num_tokens) * 100)
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Nexa Data Studio - {plan}"},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://your-hf-space-url/?success=1&job_id={job_id}",
            cancel_url=f"https://your-hf-space-url/?canceled=1&job_id={job_id}",
            metadata={"job_id": job_id, "plan": plan, "num_tokens": num_tokens}
        )
        return session.url

payment_manager = PaymentManager()