import sys
import bcrypt
import logging
import mysql.connector

from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from CMSExceptions import *


CMS_DB: MySQLConnection = None
CMS_CURSOR: MySQLCursor = None

MINIMUM_SCHEMA_QUERY = "CREATE TABLE customers (ID int PRIMARY KEY AUTO_INCREMENT, email VARCHAR(255) UNIQUE NOT NULL, name VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, address VARCHAR(255) NOT NULL, phonenumber VARCHAR(255) NOT NULL);"
MINIMUM_API_SCHEMA = "CREATE TABLE api (ID int PRIMARY KEY AUTO_INCREMENT, client_id VARCHAR(255) UNIQUE NOT NULL, hashed_client_secret VARCHAR(255) NOT NULL, is_admin TINYINT NOT NULL)"

# NON-REST FUNCTIONS

def execute_sql(query, bind_data: tuple = None, commit: bool = False) -> MySQLCursor:
    """ 
    Using temporary cursors to execute queries avoids internal error messages (I don't know why) 
    REMINDER: Use "CMS_DB.commit()" to confirm changes to the DB i.e. create, update, delete operations. 
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

# PRE-APP-ROUTINES


def pr_sql_connection(host, port, user, password, db) -> MySQLConnection:
    """ Connect to CMS MySQL Database, otherwise exit prematurely """
    global CMS_DB

    try:
        CMS_DB = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db
        )
        logging.info(f'Connection to {host}:{port} mysql made successfully')
    except Exception as e:
        logging.error(f'Connection to {host}:{port} mysql failed, ending early.')
        raise MYSQLConnectionError(host, port)
        
    return CMS_DB


def pr_schema(populate: bool = 0) -> None:
    """ 
    If POPULATE_EMPTY_DB:
        If the Database has no "customers" table then it will make one to the default viable schema.
    else:
        Raise exception with an error requiring the administrator to 
        create a "customers" table with the minimum viable table attributes.
        i.e. the primary key and any attributes used by the REST API functions for CRUD interactions
    """
    table_exists = execute_sql(f"SHOW TABLES LIKE 'customers'").fetchone()
    logging.critical("No 'customers' table in cmsdb found") if not table_exists else logging.info("'customers' table found")
    
    if not table_exists and populate:
        execute_sql(MINIMUM_SCHEMA_QUERY, commit=True)
        execute_sql(MINIMUM_API_SCHEMA, commit=True)
        logging.info("'customers' and 'api' table created with minimum necessary schema ")

    logging.info(f"'customers' table must have the following for API usages:\n{MINIMUM_SCHEMA_QUERY}")

    if not table_exists and not populate:
        raise MissingTableError(f"'customers' table does not exist, throwing exception. Create a table with the following minimum schema:\n{MINIMUM_SCHEMA_QUERY}")

# REST API RELATED FUNCTIONS

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