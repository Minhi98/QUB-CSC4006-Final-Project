import jwt
import requests

from forms import *
from vars import *

from functools import wraps
from flask import redirect, url_for, request, make_response, flash



def base_template(f):
    """
    Decorator function for the Base Template
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        kwargs['user_details'] = {}
        jwt_cookie = request.cookies.get('loginJWT', None)
        if jwt_cookie:
            kwargs['user_details'] = requests.get(
                url=f"{INTEGRATION}/user",
                headers=HEADERS|{"Authorization": f"Bearer {jwt_cookie}"}
            ).json()
        kwargs['loginJWT'] = jwt_cookie

        search_form = BaseSearchForm()
        login_form = LoginForm()
        logout_form = LogoutButton()
        kwargs['base_search_form'] = search_form
        kwargs['base_login_form'] = login_form
        kwargs['base_logout_form'] = logout_form

        if search_form.validate_on_submit() and search_form.search.data:
            return redirect(url_for('search', query=search_form.search.data))

        if login_form.validate_on_submit() and login_form.username.data and login_form.password.data:
            username = login_form.username.data
            password = login_form.password.data
            login_response = requests.get(
                url=f"{INTEGRATION}/user/login",
                headers=HEADERS,
                json={
                    "username": username,
                    "password": password
                },
                allow_redirects=False
            )
            if login_response.json()['token'] == 'deleted':
                flash("This account has been deleted.")
                return redirect(url_for('homepageRedirect'))
            login_jwt = login_response.json()['token'][0] if login_response.status_code == 200 else None
            if login_response.status_code == 200:
                set_login_cookie = make_response(redirect(url_for('homepageRedirect')))
                set_login_cookie.set_cookie('loginJWT', login_jwt)
                return set_login_cookie

        # For unknown reasons this must always be below the login_form check
        if logout_form.validate_on_submit() and logout_form.submit.data:
            logout_response = requests.delete(
                url=f"{INTEGRATION}/user/logout",
                headers=HEADERS|{"Authorization": f"Bearer {jwt_cookie}"}
            )
            if logout_response.status_code != 404:
                set_login_cookie = make_response(redirect(url_for('homepageRedirect')))
                set_login_cookie.delete_cookie('loginJWT')
                return set_login_cookie

        return f(*args, **kwargs)
    return decorated_function
