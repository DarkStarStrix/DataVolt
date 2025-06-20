"""
app/__init__.py: Exposes main backend components for reuse.
"""

from .Api import app as fastapi_app
from .Core import job_manager
from .Progress import progress_tracker
from .Payment import payment_manager

__all__ = [
    "fastapi_app",
    "job_manager",
    "progress_tracker",
    "payment_manager",
]
