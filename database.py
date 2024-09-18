import sqlite3
import os
from langchain.sql_database import SQLDatabase
import json


def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)


def create_database_from_sql():
    config = load_config()
    sql_file_path = config['database']['sql_file_path']
    db_file_path = config['database']['db_file_path']

    # Check if the database already exists
    if os.path.exists(db_file_path):
        print(f"Database already exists at {db_file_path}")
        return

    conn = sqlite3.connect(db_file_path)

    encodings = ['utf-8', 'latin-1', 'utf-16']

    for encoding in encodings:
        try:
            with open(sql_file_path, "r", encoding=encoding) as sql_file:
                sql_script = sql_file.read()
            break
        except UnicodeDecodeError:
            if encoding == encodings[-1]:
                raise
            continue

    conn.executescript(sql_script)
    conn.commit()
    conn.close()
    print(f"Database created at {db_file_path}")


def load_database():
    config = load_config()
    db_uri = config['database']['db_uri']
    return SQLDatabase.from_uri(db_uri)


def initialize_database():
    create_database_from_sql()
    db = load_database()
    print("Database loaded successfully")
    return db