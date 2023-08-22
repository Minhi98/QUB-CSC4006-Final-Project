import requests
import datetime

from var import *
from security import encode_jwt, decode_jwt

from flask import request

def get_request_jwt(request: request, decode: bool = False):
    """
    Using an endpoint's request object, return the JWT or its decoded form.

    request ::  the request object
    decode  ::  flag to decode the JWT and return it
    """
    auth_header = request.headers.get('Authorization')
    if decode:
        return decode_jwt(auth_header.split(" ")[1])
    else:
        return auth_header.split(" ")[1] if auth_header else None

def register_new_jwt(email_identity: str, expiry_offset: datetime.timedelta = None):
    """
    Encodes and stores a new JWT using the set identity (intended for emails) and of a set expiry.

    email_identity  ::  the user's email (set as the JWT subject claim)
    expiry_offset   ::  set lifetime of login JWTs, default of 24 hours.
    """
    new_jwt = encode_jwt(identity=email_identity, expiry_offset=expiry_offset)
    response = requests.post(
        url=DatastoreURL(JWT_SERVICE),
        json={ 
            "token": new_jwt,
            "blacklisted": int(False)
        }
    )
    return new_jwt, response.status_code