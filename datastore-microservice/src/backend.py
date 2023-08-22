import sys
import time
import logging
import mysql.connector

from var import *
from exceptions import *

from authlib.common.security import generate_token

from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

# CONVENIENCE FUNCTIONS

def get_table_row(search_value: str, column: str = "ID"):
    """ Returns specific row of a table """
    return execute_sql(
        f"""SELECT * FROM {SERVICE_TABLE} WHERE {column} = %s""", 
        bind_data=(search_value,)
        ).fetchone()

def get_table_row_column(row_column: str, search_value: str, search_column: str):
    """ Returns specific column of a row in a table """
    search = get_table_row(search_value, search_column)
    return search[get_table_columns().index(row_column)] if search else None

def get_table_columns():
    """ Return columns of a table """
    return [c[0] for c in execute_sql(f"DESCRIBE {SERVICE_TABLE}").fetchall()]

# SQL

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
    CMS_DB.reconnect()
    cursor = CMS_DB.cursor()
    if bind_data:
        cursor.execute(query, bind_data)
    else:
        cursor.execute(query)
    if commit:
        CMS_DB.commit()
    return cursor

# SETUP

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
    pr_check_table_exists(SERVICE_TABLE, TABLE_MIN_SCHEMA)