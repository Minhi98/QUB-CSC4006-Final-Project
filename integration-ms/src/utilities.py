import requests
import datetime

from var import *
from utilities import *

from thefuzz import fuzz
from email_validator import validate_email

def filter_from_datastore(rows, search_filter: tuple = None, unique_match: bool = True, partial_match: int = 0):
    """
    Application of filters on datastore JSON from a GET request in get_from_datastore

    rows            ::  datastore JSON from a GET request
    search_filter   ::  A tuple of (column name, expected value) that is used to search through the requested data
                        - In the case of "ID" as the column name a request is made to get the specific ID instead of the whole set.
    unique_match    ::  Flag to specify if the expected return should be unique, should only be used for known unique data such as emails
    partial_match   ::  Perform a fuzzy search and get all results that are greater or equal to the desired fuzz ratio (0 to 100 inclusive), requires search_filter.
    """
    if search_filter:
        row_filter_column = search_filter[0]
        row_filter_str = str(search_filter[1])

    if search_filter and partial_match:
        partial_matches = {k:v for k,v in rows.items() if fuzz.partial_ratio(row_filter_str, str(v[row_filter_column])) >= partial_match}
        return partial_matches
    
    if search_filter and unique_match:
        return next(({k:v} for k, v in rows.items() if str(v[row_filter_column]) == row_filter_str), None)
    
    if search_filter:
        return {k: v for k, v in rows.items() if str(v[row_filter_column]) == row_filter_str}
    
    return rows

def get_from_datastore(service_dict: dict, search_filter: tuple = None, unique_match: bool = True, partial_match: int = 0):
    """
    Performs a get request to retrieve data from a service. Either for all entries, one, or any that match an equality.

    service_dict    ::  the data of the service being passed in (see vars.py)
    search_filter   ::  A tuple of (column name, expected value) that is used to search through the requested data
                        - In the case of "ID" as the column name a request is made to get the specific ID instead of the whole set.
    unique_match    ::  Flag to specify if the expected return should be unique, should only be used for known unique data such as emails
    partial_match   ::  Perform a fuzzy search and get all results that are greater or equal to the desired fuzz ratio (0 to 100 inclusive), requires search_filter.
    """
    if search_filter and search_filter[0] == "ID":
        return requests.get(url=DatastoreURL(service_dict), json={"ID": search_filter[1]}, headers=HEADERS).json()

    rows = requests.get(url=DatastoreURL(service_dict), json={}, headers=HEADERS).json()
    return filter_from_datastore(rows, search_filter=search_filter, unique_match=unique_match, partial_match=partial_match)

def get_users(search_filter: tuple = None, unique_match: bool = True):
    """
    Wrapper function of get_from_datastore() for user data
    """
    return get_from_datastore(USERS, search_filter=search_filter, unique_match=unique_match)

def get_jwts(search_filter: tuple = None, unique_match: bool = True):
    """
    Wrapper function of get_from_datastore() for JWTs
    """
    return get_from_datastore(JWT_SERVICE, search_filter=search_filter, unique_match=unique_match)

def get_baskets(search_filter: tuple = None, unique_match: bool = True):
    """
    Wrapper function of get_from_datastore() for user baskets
    """
    return get_from_datastore(BASKETS, search_filter=search_filter, unique_match=unique_match)

def get_orders(search_filter: tuple = None, unique_match: bool = True):
    """
    Wrapper function of get_from_datastore() for stored historic orders
    """
    return get_from_datastore(ORDERS, search_filter=search_filter, unique_match=unique_match)

def get_store_inventory(search_filter: tuple = None, unique_match: bool = True, partial_match: int = 0):
    """
    Wrapper function of get_from_datastore() for store inventory
    """
    return get_from_datastore(STORE_INVENTORY, search_filter=search_filter, unique_match=unique_match, partial_match=partial_match)

def validate_arg_email(email: str):
    """ Bad request handler for emails passed into the request """
    try:
        email = validate_email(email).email
        return True
    except:
        return False

def confirm_jwt_user(jwt_sub: str):
    """
    Checks if the JWT subject exists as a user
    
    jwt_sub ::  the subject string for the JWT, in this case expected to be an email address
    """
    matched_user = get_users(("email", jwt_sub), True)
    return True if matched_user else False

def confirm_jwt_id(jwt_sub, user_id):
    """
    Intended for endpoints of /<string:user_id>" - checks if account of subject email and the user_id match.

    jwt_sub ::  JWT subject claim - email address
    user_id ::  The ID compared against
    """
    users = get_users()
    matched_user = {k:v for k,v in users.items() if v["email"] == jwt_sub}
    _id,_ = list(matched_user.items())[0]
    return bool(_id == user_id)

def check_jwt_expiry(jwt_expiry: datetime.datetime):
    return bool(datetime.datetime.utcnow().timestamp() > jwt_expiry)