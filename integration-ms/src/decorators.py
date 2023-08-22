from functools import wraps

from request_jwt import *
from security import *

def jwt_authenticate(func):
    """
    Decorator for JWT authentication
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.get('user_id', None)
        if not check_auth(get_request_jwt(request, decode=True), validating_id=user_id):
            return 403
        return func(*args, **kwargs)
    return wrapper