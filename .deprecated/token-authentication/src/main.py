import logging

from var import *
from backend import *

from flask import Flask
from flask_restful import Resource, Api, reqparse
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
api = Api(app)
oauth = OAuth(app)

CMS_DB = pr_sql_connection(
            MYSQL_HOST, 
            MYSQL_PORT, 
            MYSQL_USER, 
            MYSQL_PASS,
            MYSQL_DB,
            wait_period=5
        )
pr_schema()
new_root_pass, new_root_token = root_rotation()
logging.critical(f"ISSUING NEW ROOT PASSWORD: {new_root_pass}")
logging.critical(f"ISSUING NEW ROOT TOKEN: {new_root_token}")

token_remove_args = reqparse.RequestParser()
token_remove_args.add_argument("access_token", type=str)
token_remove_args.add_argument("target_token", type=str)
token_remove_args.add_argument("username", type=str)

issue_args = reqparse.RequestParser()
issue_args.add_argument("username", type=str)
issue_args.add_argument("password", type=str)

user_args = reqparse.RequestParser()
user_args.add_argument("access_token", type=str)
user_args.add_argument("username", type=str)
user_args.add_argument("password", type=str)
user_args.add_argument("new_username", type=str)
user_args.add_argument("new_password", type=str)

class Users(Resource):
    def post(self):
        """
        Creates User if using a valid token
        access_token    :: token 
        username        :: new user's username
        password        :: new user's password

        Example: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/user -d '{"access_token": "<token>", "username": "<name>", "password": "<pass>"}'
        """
        args = user_args.parse_args()
        if not validate_access_token(args["access_token"]):
            return {"error": "Invalid credentials"}, 401

        if get_table_row_column("users", "username", args["username"], "username"):
            return {"error": "Duplicate username"}, 400

        # To prevent any potential bugs from a username string being numeric like an ID is.
        if args["username"].isnumeric():
            return {"error": "Invalid username"}, 400

        execute_sql(
            """INSERT INTO users (ID, username, password) VALUES (NULL, %s, %s)""",
            bind_data=(
                args["username"],
                hash_password(args["password"])
            ),
            commit=True
        )

        return 201

    def put(self):
        """
        Updates User if using a valid token
        access_token    :: token 
        username        :: the target user to be updated
        new_username    :: target user's new username
        new_password    :: target user's new password for token issuing

        Example: curl -X PUT -H "Content-Type: application/json" 127.0.0.1:5000/user -d '{"access_token": "<token>", "username": "<target_user>", "new_username": "<new_name>", "new_password": "<new_pass>"}'
        """
        args = user_args.parse_args()
        if not validate_access_token(args["access_token"]):
            return {"error": "Invalid credentials"}, 401

        if get_table_row_column("users", "username", args["new_username"], "username"):
            return {"error": "new_username is a duplicate of an existing username"}, 400

        user = get_table_row("users", "username", args["username"])
        columns = get_table_columns("users")
        user = {columns[i]: user[i] for i in range(len(user))}

        execute_sql(
            """UPDATE users SET username = %s, password = %s WHERE username = %s""",
            bind_data=(
                args["new_username"] if args["new_username"] else args["username"],
                hash_password(args["new_password"] ) if args["new_password"] else user["password"],
                args["username"]
            ),
            commit=True
        )

        return 201

    def get(self):
        """
        Reads User if using a valid token and returns details
        access_token    :: token 
        username        :: the target user to be read

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/user -d '{"access_token": "<token>", "username": "<username>"}'
        """
        args = user_args.parse_args()
        if not validate_access_token(args["access_token"]):
            return {"error": "Invalid credentials"}, 401
        user = get_table_row("users", "username", args["username"])
        columns = get_table_columns("users")
        user = {columns[i]: user[i] for i in range(len(user))}
        del user["password"]

        return user, 200

    def delete(self):
        """
        Deletes User if using a valid token
        access_token    :: token 
        username        :: the target user to be deleted

        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/user -d '{"access_token": "<token>", "username": "<username>"}'
        """
        args = user_args.parse_args()
        if not validate_access_token(args["access_token"]):
            return {"error": "Invalid credentials"}, 401
        
        userID = get_table_row_column("users", "username", args["username"], "ID")
        if not userID:
            return {"error": "Invalid username"}, 400

        execute_sql(
            """DELETE FROM tokens WHERE userID = %s""", 
            bind_data=(userID,), 
            commit=True
        )
        execute_sql(
            """DELETE FROM users WHERE username = %s""", 
            bind_data=(args["username"],), 
            commit=True
        )

        return 204

class Tokens(Resource):
    def post(self):
        """
        Assuming the requester is a valid user, this will generate and store a new token. Responding with that token.
        username :: Requester username
        password :: Requester password

        Example: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/token -d '{"username": "<your_username>", "password": "<your_pass>"}'
        """
        args = issue_args.parse_args()
        username = args['username']
        password = args['password']

        # Validate credentials
        if not validate_credentials(username, password):
            return {"error": "Invalid credentials"}, 401

        # Issue access token
        access_token = issue_access_token(username)
        return {"access_token": access_token}, 201

    def delete(self):
        """
        If only provided a token, deletes all rows with that token (0 or 1).
        If only provided a username, deletes all tokens of that user (0+).
        If provided both a token and username, deletes that token if it belongs to that user (0+).
        access_token    :: token for access to this function
        target_token    :: token to be deleted
        username        :: filter to delete all tokens of user, or specific token of user

        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/token -d '{"access_token": "<token>", "target_token": "<token>"}'
        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/token -d '{"access_token": "<token>", "username": "<username>"}'
        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/token -d '{"access_token": "<token>", "username": "<userID>"}'
        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/token -d '{"access_token": "<token>", "username": "<username or userID>", "target_token": "<target_token>"}'
        """
        args = token_remove_args.parse_args()
        if not validate_access_token(args["access_token"]):
            return {"error": "Invalid credentials"}, 401
        
        token = args["target_token"]
        userID = args["username"]
        if userID and not userID.isnumeric():
            userID = get_table_row_column("users", "username", userID, "ID")

        if token and not userID:
            execute_sql(
                """DELETE FROM tokens WHERE token = %s""",
                bind_data=(token,),
                commit=True
            )
            return 204

        if not token and userID:
            execute_sql(
                """DELETE FROM tokens WHERE userID = %s""",
                bind_data=(userID,),
                commit=True
            )
            return 204

        if token and userID:
            execute_sql(
                """DELETE FROM tokens WHERE token = %s AND userID = %s""",
                bind_data=(token, userID),
                commit=True
            )
            return 204

        return 404

api.add_resource(Tokens, '/token')
api.add_resource(Users, '/user')

if __name__ == "__main__":
    # Only run flask for development "flask --app main.py --debug run"
    app.run(host="0.0.0.0", port="5000", debug=True)