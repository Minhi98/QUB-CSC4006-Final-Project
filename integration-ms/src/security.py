import jwt 
import bcrypt
import datetime

from var import JWT_SERVICE
from utilities import *

def check_auth(decoded_jwt: dict, validating_id = None):
    """
    Runs verification checks on the jwt.
    Performs initial verifications and then compares the expiry against current time.

    Returns True if pre_checks remains True and the token is within its expiry datetime.
    """
    pre_checks = [confirm_jwt_user(decoded_jwt["sub"])]
    
    if validating_id:
        pre_checks.append((validating_id and confirm_jwt_id(decoded_jwt["sub"], validating_id)))

    if not check_jwt_expiry(decoded_jwt["exp"]) and all(pre_checks):
        return True
    return False

# Bcrypt encode and validate

def hash_password(password: str) -> str:
    """ Salts and hashes passwords """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password) -> bool:
    """ Check hashed password against plain text, password should be pre-pulled from user row """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def hash(input: str) -> str:
    """ Wrapper of hash_password for readability """
    return hash_password(input)

def compare_hashed(non_hashed_string: str, hashed_string: str) -> bool:
    """ Wrapper of check_password for readability """
    return check_password(non_hashed_string, hashed_string)

# JWT functions

def encode_jwt(identity: str, expiry_offset: datetime.timedelta=None) -> str:
    """
    Generates a JWT Token.
    Payload keys are based off JWT Claims 
    - https://www.digitalocean.com/community/tutorials/the-anatomy-of-a-json-web-token#payload

    identity        ::  the identity of the JWT, for this service that is the user's email address
    expiry_offset   ::  the lifetime of the JWT, default is 24 hours.
    """
    if expiry_offset is None:
        expiry_offset = datetime.timedelta(days=1)

    return jwt.encode(
        payload={
            'exp': datetime.datetime.utcnow() + expiry_offset,
            'iat': datetime.datetime.utcnow(),
            'sub': identity,
        },
        key=JWT_SERVICE["SECRET"],
        algorithm=JWT_ENCODING
    )

def decode_jwt(jwt_token: str):
    """
    Decodes the jwt token.

    jwt_token   ::  A JWT as an encoded string
    """
    try:
        # returning the whole payload as certain endpoints need more than the subject claim key
        return jwt.decode(jwt_token, JWT_SERVICE["SECRET"], algorithms=[JWT_ENCODING])
    except jwt.PyJWKError:
        return None