from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "50/hour"])

def get_limiter():
    return limiter
