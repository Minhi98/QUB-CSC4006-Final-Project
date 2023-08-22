import os

from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection

MYSQL_HOST = os.environ.get('MYSQL_HOST', "csc4006")
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3300)
MYSQL_USER = os.environ.get('MYSQL_USER', "root")
MYSQL_PASS = os.environ.get('MYSQL_PASS', "4006")
MYSQL_DB = os.environ.get('MYSQL_DB', "authdb")

USERS_SCHEMA = """CREATE TABLE users (
    ID int PRIMARY KEY AUTO_INCREMENT, 
    username VARCHAR(255) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL
    );"""

TOKENS_SCHEMA = """CREATE TABLE tokens (
    ID int PRIMARY KEY AUTO_INCREMENT, 
    userID int NOT NULL, 
    token VARCHAR(255) UNIQUE NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(ID)
    );"""

# ID = 1 and username = "root" for the root account is immutable by design
ROOT_USER_QUERY = \
        f"""INSERT INTO users (ID, username, password) 
        VALUES (1, 'root', %s) 
        ON DUPLICATE KEY UPDATE ID=1, username='root', password=%s;"""
ROOT_TOKEN_QUERY = \
        f"""INSERT INTO tokens (ID, userID, token)
        VALUES (1, 1, %s)
        ON DUPLICATE KEY UPDATE ID=1, userID=1, token=%s;"""

CMS_DB: MySQLConnection = None
CMS_CURSOR: MySQLCursor = None
