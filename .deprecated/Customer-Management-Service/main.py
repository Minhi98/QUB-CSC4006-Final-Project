import os
import time
import logging
import mysql.connector.errorcode as sql_error_codes

from flask import Flask, request
from CMSFunctions import *
from flask_restful import Resource, Api, abort, reqparse
from email_validator import validate_email, EmailNotValidError
from mysql.connector.errors import IntegrityError, ProgrammingError


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

CUSTOMER_TABLE: str = "customers"
API_TABLE: str = "api"

# ENV VARS SET FROM DOCKER
MYSQL_HOST = os.environ.get('MYSQL_HOST', "csc4006")
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_USER = os.environ.get('MYSQL_USER', "root")
MYSQL_PASS = os.environ.get('MYSQL_PASS', "4006")
MYSQL_DB = os.environ.get('MYSQL_DB', "cmsdb")
POPULATE_EMPTY_DB = os.environ.get('POPULATE_EMPTY_DB', 1)

while True:
    try:
        CMS_DB = pr_sql_connection(
            MYSQL_HOST, 
            MYSQL_PORT, 
            MYSQL_USER, 
            MYSQL_PASS,
            MYSQL_DB
        )
        if CMS_DB.is_connected():
            break
    except Exception as e:
        time.sleep(10)

pr_schema(populate = POPULATE_EMPTY_DB)

app = Flask("Customer Management Service")
api = Api(app)

customer_args = reqparse.RequestParser()
# AUTH ARGS FOR USING THE API
customer_args.add_argument("id", type=str)
customer_args.add_argument("secret", type=str)
# REST API ARGS
customer_args.add_argument('email', type=str)
customer_args.add_argument('name', type=str)
customer_args.add_argument('password', type=str)
customer_args.add_argument('encrypted', type=bool)
customer_args.add_argument('address', type=str)
customer_args.add_argument('phonenumber', type=str)

api_args = reqparse.RequestParser()
api_args.add_argument("id", type=str)
api_args.add_argument("secret", type=str)
api_args.add_argument("admin", type=bool)
api_args.add_argument("target", type=str)
api_args.add_argument("new_client_id", type=str)
api_args.add_argument("new_client_secret", type=str)

# Abort codes correspond to HTTP Response Status Codes - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

def check_table_exists(table: str):
    """ Confirms table exists, aborts as a server-side error if not """
    desc = execute_sql(f"DESCRIBE {table}").fetchall()
    if not desc:
        abort(501, desc=f"{table} table does not exist")
    
    if table == CUSTOMER_TABLE:
        return [d[0] for d in desc][2:]
    
    return [d[0] for d in desc]

def check_row_exists(id: str, table: str, column: str):
    """ Searches for user, returns their row - aborts if fetchone returns None results """
    result = execute_sql(f"""SELECT * FROM {table} WHERE {column} = %s""", bind_data=(id,)).fetchone()
    if not result:
        abort(404, desc=f"{id} does not exist")
    return result

def validate_arg_email(email: str):
    """ Bad request handler for emails passed into the request """
    try:
        email = validate_email(email).email
    except EmailNotValidError as e:
        abort(400, desc="Email address is not valid")

def auth_check(id: str, secret: str, admin_required: bool = True, \
    api_table: str = "api", api_id_column: str = "client_id", api_secret_column:str = "hashed_client_secret", api_admin_column:str = "is_admin"):
    """ Checks if the api key exists and compares secrets, aborts if they are not the same """
    id_row = check_row_exists(id=id, table=api_table, column=api_id_column)
    desc = check_table_exists(api_table)

    secret_comparison = compare_hashed(non_hashed_string=secret, hashed_string=id_row[desc.index(api_secret_column)])
    if not secret_comparison:
        abort(403, desc=f"Unathorised access")
    if admin_required:
        if not bool(id_row[desc.index(api_admin_column)]):
            abort(403, desc=f"Unathorised access")

# REST API Classes

class Auth(Resource):
    
    def post(self):
        """
        Creates an API Key and stores it into the service, only admins can make new admins
        Example Request: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"new_client_id": "non_admin_test", "new_client_secret": "non_admin_pass123"}'
        Example Request: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "admin_test", "secret": "admin_pass123", "new_client_id": "new_admin", "new_client_secret": "admin_pass234", "admin": true}'
        """
        check_table_exists(table=API_TABLE)
        args = api_args.parse_args()
        
        if execute_sql(f"""SELECT * FROM {API_TABLE} WHERE client_id = %s""", bind_data=(args["new_client_id"],)).fetchone():
            abort(400, desc="Bad Request, ID exists")
        
        new_api_key = {
            "id": args["new_client_id"],
            "secret": hash(args["new_client_secret"])
        }

        if args["admin"]:
            auth_check(id=args["id"], secret=args["secret"], admin_required=True)
            new_api_key["admin"] = int(args["admin"])
        else:
            new_api_key["admin"] = 0
        
        execute_sql(
            f"""INSERT INTO {API_TABLE} (client_id, hashed_client_secret, is_admin) VALUES (%s, %s, %s)""",
            bind_data=(new_api_key["id"], new_api_key["secret"], new_api_key["admin"]),
            commit=True
        )

        del new_api_key["secret"]
        return new_api_key, 201

    def get(self):
        """
        Retrieves details of stored client.
        Admins permissions only, unless viewing your own details
        Example Request: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target": "non_admin_test"}'
        Example Request: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "non_admin_test", "secret": "non_admin_pass123", "target": "non_admin_test"}'
        """
        args = api_args.parse_args()
        if args["id"] != args["target"]:
            auth_check(id=args["id"], secret=args["secret"], admin_required=True)
        desc = check_table_exists(table=API_TABLE)
        result = check_row_exists(args["target"], table=API_TABLE, column="client_id")

        user = {desc[i]:result[i] for i in range(len(result))}
        del user["ID"]
        del user["hashed_client_secret"]

        return user, 200

    def put(self):
        """
        Set a new secret key for the client id
        Example request: curl -X PUT -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target": "non_admin_test", "new_client_id": "edit_test", "new_client_secret": "edit_pass", "admin": true}'
        """
        args = api_args.parse_args()
        admin_check = False
        if (args["id"] != args["target"]) or args["admin"]:
            auth_check(id=args["id"], secret=args["secret"], admin_required=True)
            admin_check = True

        desc = check_table_exists(API_TABLE)
        client = check_row_exists(args["target"], table=API_TABLE, column="client_id")

        execute_sql(
            f"""UPDATE {API_TABLE} SET client_id = %s, hashed_client_secret = %s, is_admin = %s WHERE client_id = %s""", 
            bind_data=(
                args['new_client_id'] if args['new_client_id'] else client[desc.index("client_id")],
                hash_password(args['new_client_secret']) if args['new_client_secret'] else client[desc.index("hashed_client_secret")],
                args['admin'] if admin_check else client[desc.index("is_admin")],
                args["target"]
            ),
            commit=True
        )

        return 201
    
    def delete(self):
        """
        Deletes an existing API key
        Example Request (intended to fail): curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "non_admin_test", "secret": "non_admin_pass123", "target":"admin_test"}'
        Example Request: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target":"non_admin_test"}'
        """
        args = api_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=True)
        check_table_exists(table=API_TABLE)

        execute_sql(f"""DELETE FROM {API_TABLE} WHERE client_id = %s""", bind_data=(args["target"],), commit=True)
        return 204

class Customer(Resource):

    def get(self, email_id):
        """
        Return customer by Email ID, 0 or 1 results.
        Example request: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/customer/new_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123"}'
        """
        args = customer_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=False)
        validate_arg_email(email_id)
        desc = check_table_exists(CUSTOMER_TABLE)
        result = check_row_exists(email_id, table=CUSTOMER_TABLE, column="email")
        
        email = result[1]
        result = result[2:]
        customer = {email: {desc[i]:result[i] for i in range(len(result))}}
        for e in customer.keys():
            customer[e].pop("password")
        
        return customer, 200

    def post(self, email_id):
        """
        Add a new customer (args: name, password (+ optional pre-encrypted flag), address, phonenumber)
        Example request: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/customer/new_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "name": "new_test", "password": "123", "address": "bt12 123", "phonenumber": "123"}'
        Example request: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/customer/new_customer2@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "name": "new_test", "password": "123", "encrypted": "True", "address": "bt12 123", "phonenumber": "123"}'
        """
        args = customer_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=False)
        check_table_exists(CUSTOMER_TABLE)
        validate_arg_email(email_id)
        
        data = (
            email_id,
            args['name'],
            args['password'] if args['encrypted'] else hash_password(args['password']),
            args['address'],
            args['phonenumber']
        )

        execute_sql(f"""INSERT INTO {CUSTOMER_TABLE} (email, name, password, address, phonenumber) VALUES (%s, %s, %s, %s, %s)""", data, commit=True)

        return 201

    def put(self, email_id):
        """
        Updates existing customer details to arguments passed, if argument is None for a column's arg then that's retained
        Example request curl -X PUT -H "Content-Type: application/json" 127.0.0.1:5000/customer/new_customer2@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "email": "edit_customer@test.com", "name": "new_test", "password": "123", "address": "bt12 123", "phonenumber": "123"}'
        """
        args = customer_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=False)
        desc = check_table_exists(CUSTOMER_TABLE)
        validate_arg_email(email_id)
        user = check_row_exists(email_id, table=CUSTOMER_TABLE, column="email")

        password = args["password"]
        if not args["password"]:
            password = user[desc.index("password")]
        elif args["password"]:
            password = args["password"] if args['encrypted'] else hash_password(args["password"])

        data = (
            args['email'] if args['email'] else email_id, # new email
            args['name'] if args['name'] else user[desc.index("name")], # new name
            password, #new password (see above for how its set)
            args['address'] if args['address'] else user[desc.index("address")], # new address
            args['phonenumber'] if args['phonenumber'] else user[desc.index("phonenumber")], # new phonenumber
            email_id #queried email
        )

        execute_sql(f"""UPDATE {CUSTOMER_TABLE} SET email = %s, name = %s, password = %s, address = %s, phonenumber = %s WHERE email = %s""", bind_data=data, commit=True)

        return 201
    
    def delete(self, email_id):
        """
        Delete a user by their email ID
        Example request curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/customer/edit_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123"}'
        """
        args = customer_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=False)
        check_table_exists(CUSTOMER_TABLE)
        validate_arg_email(email_id)

        execute_sql(f"""DELETE FROM {CUSTOMER_TABLE} WHERE email = %s""", bind_data=(email_id,), commit=True)
        return 204

class CustomerManagement(Resource):

    def get(self):
        """
        Return all customers or a specific customer
        Example request curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/customers -d '{"id": "admin_test", "secret": "admin_pass123"}'
        """
        args = customer_args.parse_args()
        auth_check(id=args["id"], secret=args["secret"], admin_required=False)
        desc = check_table_exists(CUSTOMER_TABLE)
        results = execute_sql(f"SELECT * FROM {CUSTOMER_TABLE}").fetchall()
        
        customers = {}
        for res in results:
            _id = res[1]
            res = res[2:]
            values = {desc[i]:res[i] for i in range(len(res))}
            del values["password"]
            customers.update({_id: values})
        
        return customers, 200

# Resource Routes

api.add_resource(Auth, '/auth')
api.add_resource(CustomerManagement, '/customers')
api.add_resource(Customer, '/customer/<email_id>')


@app.errorhandler(ProgrammingError)
@app.errorhandler(IntegrityError)
def handle_mysql_errors(e):
    # Error handling for SQL related bugs (if your request results in this, then there is a critical bug or flaw)
    sql_error_code = str(e).split(' ')[0]
    return {
        "SQL_ERROR_CODE": sql_error_code,
        "REASON": str(e).split('): ')[1]
    }


if __name__ == "__main__":
    # Only run flask for development "flask --app main.py --debug run"
    app.run(host="0.0.0.0", port="5000", debug=True)