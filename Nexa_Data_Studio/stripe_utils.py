import uuid

# Simulated Stripe logic for Hugging Face Spaces
PAID_SESSIONS = set()

PLAN_PRICES = {
    "Starter": 5,
    "Pro": 15,
    "Custom": None,  # Custom handled separately
}

PRODUCT_IDS = {
    "Starter": "prod_starter_id",
    "Pro": "prod_pro_id",
    "Custom": "prod_custom_id",
}

def create_checkout_session(plan, email=None, custom_price=None):
    """
    Simulate Stripe checkout. Returns a session_id and a fake payment link.
    """
    session_id = str(uuid.uuid4())
    price = PLAN_PRICES.get(plan, custom_price)
    link = f"https://buy.stripe.com/test_{session_id[:8]}"  # Fake link
    return {"session_id": session_id, "checkout_url": link, "price": price}

def verify_payment(session_id):
    """
    Simulate payment verification. Always returns True for demo.
    """
    PAID_SESSIONS.add(session_id)
    return True

