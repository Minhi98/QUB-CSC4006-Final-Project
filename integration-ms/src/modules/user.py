import json
import requests

from var import *
from security import *
from utilities import *
from request_jwt import *
from decorators import *

from flask import request
from flask_restful import Resource, reqparse

class CurrentUser(Resource):
    @jwt_authenticate
    def get(self):
        """
        Returns details of currently logged in user (dependent on JWT)
        
        Example: curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user
        """
        jwt = get_request_jwt(request, decode=True)
        
        matched_user = get_users(("email", jwt["sub"]), True)
        if not matched_user:
            return {'error': 'User not found'}, 404
        
        _id,columns = list(matched_user.items())[0]
        del columns["password"]
        details = columns|{"ID":_id}
        return details, 200

class UserSpecific(Resource):
    @jwt_authenticate
    def put(self, user_id):
        """
        Changes the user's account details. 
        If the email is changed then a new token is issued so they can remain logged in.

        Example: curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/<id> -d '{"email": "<email>", "username": "<user>", "password": "<pass>", "address": "<addr>"}'

        email       ::  the user's email address (must be unique)
        username    ::  the user's username (must be unique)
        password    ::  the user's password (plain text, encrypted by this endpoint, should always be transferred over https in prod)
        address     ::  the user's address 
        """
        user_args = reqparse.RequestParser()
        user_args.add_argument("email", type=str, default=None)
        user_args.add_argument("username", type=str, default=None)
        user_args.add_argument("password", type=str, default=None)
        user_args.add_argument("address", type=str, default=None)
        args = user_args.parse_args()

        if args["password"]:
            args["password"] = hash_password(args["password"])
        if args["email"] and not validate_arg_email(args["email"]):
            return {'error': 'Email is not valid.'}, 400

        matched_email = get_users(("email", args["email"]), True)
        matched_username = get_users(("username", args["username"]), True)

        if matched_email:
            return {'error': 'Email is not unique.'}, 400
        if matched_username:
            return {'error': 'Username is not unique.'}, 400

        optional_jwt = {}
        if args["email"]:
            optional_jwt = {'token': register_new_jwt(args["email"])}

        args = {k:v for k,v in args.items() if v is not None}
        args.update({"ID": user_id})
        response = requests.put(url=DatastoreURL(USERS), json=args, headers=HEADERS)        
        return optional_jwt, response.status_code
    
    @jwt_authenticate
    def delete(self, user_id):
        """
        Deletes the current user's account

        Example: curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/<id>
        """
        jwt = get_request_jwt(request, decode=True)
        
        matched_user = get_users(("email", jwt["sub"]), True)
        if matched_user is None:
            return 500
        
        _id,_ = list(matched_user.items())[0]
        response = requests.put(
            url=DatastoreURL(USERS),
            headers=HEADERS,
            json={"ID": _id, "deleted": 1}
        )
        return response.status_code

class UserRegistration(Resource):
    def post(self):
        """
        Takes the inputted information and registers a new user to the user accounts microservice.
        If inputs are valid, a new token is registered and returned for an immediate login into the user's account.

        Example: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/user/register -d '{"email": "<email>", "username":"<user>", "password":"<pass>", "address":"<addr>"}'

        email       ::  the user's email address (must be unique)
        username    ::  the user's username (must be unique)
        password    ::  the user's password (plain text, encrypted by this endpoint, should always be transferred over https in prod)
        address     ::  the user's address 
        """

        registration_args = reqparse.RequestParser()
        registration_args.add_argument("email", type=str)
        registration_args.add_argument("username", type=str)
        registration_args.add_argument("password", type=str)
        registration_args.add_argument("address", type=str)
        args = registration_args.parse_args()

        args["password"] = hash_password(args["password"])
        if not validate_arg_email(args["email"]):
            return {'error': 'Email is not valid.'}, 400

        matched_email = get_users(("email", args["email"]), True)
        matched_username = get_users(("username", args["username"]), True)

        if matched_email:
            return {'error': 'Email is not unique.'}, 400
        if matched_username:
            return {'error': 'Username is not unique.'}, 400

        args["deleted"] = 0
        user_response = requests.post(url=DatastoreURL(USERS), json=args, headers=HEADERS)
        return user_response.status_code

class UserLogin(Resource):
    def get(self):
        """
        Validates the user's login credentials and returns an access token to log them in if valid

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/user/login -d '{"username": "<username>", "password": "<password>"}'

        username    ::  input username
        password    ::  input password
        """

        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        users = get_users()
        matched_account = next((v for v in users.values() if v["username"] == args["username"]), None)

        if matched_account:
            if int(matched_account["deleted"]) == 1:
                return {'token': 'deleted'}, 404
            if check_password(args["password"], matched_account["password"]):
                new_jwt = register_new_jwt(matched_account["email"])
                return {'token': new_jwt}, 200

        return 401

class UserLogout(Resource):
    def delete(self):
        """
        Logs out the user by blacklisting their current jwt.
        Example: curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/logout
        """
        jwt_token = get_request_jwt(request, decode=False)
        matched_row = get_jwts(("token", jwt_token), True)
        if matched_row:
            k,v = list(matched_row.items())[0]
            response = requests.put(
                url=DatastoreURL(JWT_SERVICE),
                json={
                    "ID": k,
                    "token": v["token"],
                    "blacklisted": int(True)
                }, 
                headers=HEADERS
            )
            return response.status_code
        else:
            return 404
