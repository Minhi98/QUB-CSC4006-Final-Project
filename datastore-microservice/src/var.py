import os
import json
import datetime

from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

CMS_DB: MySQLConnection = None
CMS_CURSOR: MySQLCursor = None

# MYSQL CONNECTION ENV VARS
MYSQL_HOST = os.environ.get('MYSQL_HOST', "csc4006")
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3299)
MYSQL_USER = os.environ.get('MYSQL_USER', "root")
MYSQL_PASS = os.environ.get('MYSQL_PASS', "4006")
MYSQL_DB = os.environ.get('MYSQL_DB', "testdb")

# REQUIRED: SERVICE_TABLE is used for CRUD requests.
SERVICE_TABLE = os.environ.get('SERVICE_TABLE', "undefined_table_name")

# OPTIONAL: TABLE_MIN_SCHEMA is only for initialisation of SERVICE_TABLE if it doesn't exist. The only truly required field is the ID.
JSON_TABLE_MIN_SCHEMA = json.loads(os.environ.get('JSON_TABLE_MIN_SCHEMA', '{"test_field1": "VARCHAR(255) NOT NULL", "test_field2":"int"}')) 
TABLE_MIN_SCHEMA = f"CREATE TABLE {SERVICE_TABLE} (ID int PRIMARY KEY AUTO_INCREMENT"
for column, props in JSON_TABLE_MIN_SCHEMA.items():
    TABLE_MIN_SCHEMA = TABLE_MIN_SCHEMA + f", {column} {props}"
TABLE_MIN_SCHEMA = TABLE_MIN_SCHEMA + ");"

# conversion of the most common types
mysql_to_python = {
    'tinyint': int,
    'smallint': int,
    'mediumint': int,
    'int': int,
    'bigint': int,
    'float': float,
    'double': float,
    'decimal': float,
    'date': datetime.date,
    'datetime': datetime.datetime,
    'timestamp': datetime.datetime,
    'time': datetime.time,
    'year': int,
    'char': str,
    'varchar': str,
    'tinytext': str,
    'text': str,
    'mediumtext': str,
    'longtext': str,
    'tinyblob': bytes,
    'blob': bytes,
    'mediumblob': bytes,
    'longblob': bytes,
    'enum': str,
    'set': str
}
