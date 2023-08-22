import sys
import time
import bcrypt
import logging
import secrets
import mysql.connector

from var import *
from exceptions import *

from authlib.common.security import generate_token

from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

# Tokens

def validate_credentials(username, password) -> bool:
    """ Finds hashed password of username in users table, and returns the comparison """
    hashed_password = get_table_row_column("users", "username", username, "password")
    if not hashed_password:
        return False
    return check_password(password, hashed_password)

def issue_access_token(username) -> str:
    """ Writes new token to tokens table, assigning UserID to ID of username in users """
    token = generate_token()
    userID = get_table_row_column("users", "username", username, "ID")

    query = """INSERT INTO tokens (ID, userID, token) VALUES (NULL, %s, %s)"""
    execute_sql(query, bind_data=(userID, token), commit=True)
    return token

def validate_access_token(access_token) -> bool:
    """ Compare access tokens between input and DB """
    token = get_table_row_column("tokens", "token", access_token, "token")
    if not token:
        return False
    if token == access_token:
        return True
    return False

# SQL

def get_table_row(table: str, id_column: str, id_search: str):
    """ Returns specific row of a table """
    search = execute_sql(
        f"""SELECT * FROM {table} WHERE {id_column} = %s""", 
        bind_data=(id_search,)
        ).fetchone()
    return search

def get_table_row_column(table: str, id_column: str, id_search: str, column: str):
    """ Returns specific column of a row in a table """
    search = get_table_row(table, id_column, id_search)
    if not search:
        return None
    columns = get_table_columns(table)
    return search[columns.index(column)]

def get_table_columns(table: str):
    """ Return columns of a table """
    return [c[0] for c in execute_sql(f"DESCRIBE {table}").fetchall()]

def execute_sql(query, bind_data: tuple = None, commit: bool = False) -> MySQLCursor:
    """
    AIO SQL query wrapper function
    query       :: SQL Query
    bind_data   :: Use for input data to protect against SQL Injections w/ mysqldb's builtin checks
    commit      :: Set as True if your query writes data to the MySQL DB
    """
    if not CMS_DB:
        raise Exception("Connect to the MySQL Database before executing queries")
    
    logging.info(f'Executing SQL from function {sys._getframe(1).f_code.co_name} -> {query}')
    
    cursor = CMS_DB.cursor()
    if bind_data:
        cursor.execute(query, bind_data)
    else:
        cursor.execute(query)
    if commit:
        CMS_DB.commit()
    return cursor

def pr_sql_connection(host, port, user, password, db, wait_period: int = 5) -> MySQLConnection:
    """ Connect to CMS MySQL Database, otherwise exit prematurely """
    global CMS_DB

    while True:
        try:
            CMS_DB = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db
            )
            if CMS_DB.is_connected():
                logging.info(f'Connection to {host}:{port} mysql made successfully')
                return CMS_DB
        except Exception as e:
            logging.error(f'Connection to {host}:{port} mysql failed, waiting to try again.')
        time.sleep(wait_period)


def pr_check_table_exists(table: str, populate_sql: str = None):
    table_exists = execute_sql(f"SHOW TABLES LIKE '{table}'").fetchone()

    logging.critical(f"No '{table}' table in cmsdb found") if not table_exists else logging.info(f"'{table}' table found")
    if populate_sql:
        logging.critical(f"'{table}' table must have the following for API usages:\n{populate_sql}")

    if not table_exists and populate_sql:
        execute_sql(populate_sql, commit=True)
        logging.info(f"'{table}' table created with minimum necessary schema ")
    
    if not table_exists and not populate_sql:
        raise MissingTableError(f"'{table}' table does not exist.")


def pr_schema():
    pr_check_table_exists('users', USERS_SCHEMA)
    pr_check_table_exists('tokens', TOKENS_SCHEMA)

def root_rotation():
    """ Rotates Root user password and token every time it starts """
    random_password = secrets.token_hex(16)
    hashed = hash_password(random_password)
    token = generate_token()
    execute_sql(query=ROOT_USER_QUERY, bind_data=(hashed, hashed), commit=True)
    execute_sql(query=ROOT_TOKEN_QUERY, bind_data=(token, token), commit=True)

    return random_password, token

# Encryption

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