"""
Config.py: Configuration for plan limits, pricing, and app constants.
"""

# Plan limits (tokens per plan)
PLAN_LIMITS = {
    "free": 1000,
    "starter": 5000,
    "pro": 10000,
    "enterprise": 100000,
}

# Pricing per plan (USD)
PLAN_PRICING = {
    "free": 0,
    "starter": 15,
    "pro": 30,
    "enterprise": "custom",
}

# Other app-wide constants
tmp_dir = "./tmp_datasets"

# Stripe keys, etc. (to be set via environment variables in production)
STRIPE_API_KEY = None