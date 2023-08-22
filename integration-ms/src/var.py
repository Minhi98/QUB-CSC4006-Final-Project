import os

# CONSTANTS

HEADERS = {'Accept': 'application/json'}
JWT_ENCODING = 'HS256'

# Microservice connection vars
# URL -> The domain name (and port if local, over direct ip etc.)
# HTTPS -> For internal requests, explicitly state if done over https or not
# SECRET -> Only necessary in cases where a secret string is needed 
#           (such as JWT which needs a key string for encoding and decoding)

# Auth
AUTH = {
    "URL": os.environ.get('AUTH_URL', ""),
    "HTTPS": os.environ.get('AUTH_HTTPS', True)
}

# Users
USERS = {
    "URL": os.environ.get('USERS_HOST', ""),
    "HTTPS": os.environ.get('USERS_HTTPS', True),
}

# JWT Tokens (for user authentication)
JWT_SERVICE = {
    "URL": os.environ.get('JWT_HOST', ""),
    "HTTPS": os.environ.get('JWT_HTTPS', True),
    "SECRET": os.environ.get('JWT_SECRET', None)
}

# Store Inventory
STORE_INVENTORY = {
    "URL": os.environ.get('STORE_INV_HOST', ""),
    "HTTPS": os.environ.get('STORE_INV_HTTPS', True),
}

# User Baskets
BASKETS = {
    "URL": os.environ.get('BASKETS_HOST', ""),
    "HTTPS": os.environ.get('BASKETS_HTTPS', True),
}

# Order History
ORDERS = {
    "URL": os.environ.get('ORDERS_HOST', ""),
    "HTTPS": os.environ.get('ORDERS_HTTPS', True),
}

# Services list
SERVICES = {
    "Token Authentication": AUTH,
    "User Accounts": USERS,
    "JWT Token Management": JWT_SERVICE,
    "Store Stock Inventory": STORE_INVENTORY,
    "User Baskets": BASKETS,
    "Order History": ORDERS
}

# Utilities

def URL(service) -> str:
    """
    Returns the URL for http/https of the provided service

    service ::  the service dictionary
    """
    protocol = "https://" if service["HTTPS"] else "http://"
    return protocol + service["URL"]

def DatastoreURL(service) -> str:
    """
    Wrapper function of URL(), used for services that use the minhi98/4006-datastore image.
    """
    return URL(service) + "/data"