# database/connection.py

# database/connection.py

import os
import json
import sys
import traceback
import psycopg2
from pathlib import Path

class Database:
    def __init__(self):
        self.connection = None
        self._config = None  # Cache for config after loading

    def _load_config(self):
        if self._config:
            return self._config

        # Try environment variables first
        config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432')
        }

        if all(config.values()):
            self._config = config
            return config

        # Try config.json in multiple locations
        possible_paths = [
            Path(getattr(sys, '_MEIPASS', '.')) / "database" / "config.json",
            Path(__file__).parent / "config.json",
            Path(sys.executable).parent / "database" / "config.json",
            Path(sys.executable).parent / "config.json"
        ]

        for config_path in possible_paths:
            try:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        file_config = json.load(f)
                    # Merge with env vars (env has higher priority)
                    for key in ['dbname', 'user', 'password', 'host', 'port']:
                        if os.getenv(f"DB_{key.upper()}"):
                            file_config[key] = os.getenv(f"DB_{key.upper()}")
                    self._config = file_config
                    print(f"[DEBUG] Loaded config from {config_path}")
                    return file_config
            except Exception as e:
                print(f"[WARNING] Could NOT load config from {config_path}: {e}")

        # Fallback to default values (for dev only — not recommended for production)
        fallback_config = {
            'dbname': 'DB_PAPERSYNC',
            'user': 'postgres',
            'password': 'papersync2025',
            'host': 'localhost',
            'port': '5432'
        }
        print("[WARNING] Using fallback configuration. Consider using config.json or environment variables.")
        self._config = fallback_config
        return fallback_config

    def connect(self):
        """Establish connection to PostgreSQL DB"""
        if self.connection and not self.connection.closed:
            return self.connection

        config = self._load_config()

        try:
            self.connection = psycopg2.connect(
                dbname=config['dbname'],
                user=config['user'],
                password=config['password'],
                host=config['host'],
                port=config['port']
            )
            print("[INFO] Successfully connected to PostgreSQL")
            return self.connection
        except Exception as e:
            print("[ERROR] Failed to connect to PostgreSQL:")
            traceback.print_exc()
            raise ConnectionError(f"Database connection failed: {e}")

    def get_cursor(self):
        if not self.connection or self.connection.closed:
            self.connect()
        return self.connection.cursor()

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("[INFO] Database connection closed")

    def get_user_first_name(self, username):
        try:
            cursor = self.get_cursor()
            cursor.execute("SELECT STAFF_FIRSTNAME FROM STAFF WHERE STAFF_USERNAME = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"[ERROR] Failed to fetch user name: {e}")
            return None
            
    def get_cursor(self):
        if self.connection:
            return self.connection.cursor()
        else:
            raise Exception("No active database connection.")

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()  # Rollback in case of an error

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def get_user_first_name(self, username):
        # Get cursor and execute query
        cursor = self.get_cursor()
        cursor.execute("SELECT STAFF_FIRSTNAME FROM STAFF WHERE STAFF_USERNAME = %s", (username,))
        
        # Fetch the result
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Return the first name
        else:
            return None  # Return None if no user found
    
    
    
    # database/connection.py
    def get_staff_id(self, username):
        cursor = self.get_cursor()
        cursor.execute("SELECT STAFF_ID FROM STAFF WHERE STAFF_USERNAME = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    # In your connection.py
    def get_staff_name_by_id(self, staff_id):
        """Get staff full name by ID, returns None if not found"""
        if staff_id is None:
            return None
            
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT STAFF_FIRSTNAME, STAFF_LASTNAME FROM STAFF WHERE STAFF_ID = %s", 
                    (staff_id,)
                )
                result = cur.fetchone()
                
                if result:
                    firstname, lastname = result
                    return f"{firstname} {lastname}".strip()
                return None
        except Exception as e:
            print(f"Error fetching staff name (ID: {staff_id}): {e}")
            return None

    def fetch_all(self, query, params=None):
        if not self.connection:
            raise Exception("Database connection is not established.")
        cursor = self.get_cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return results
    
    def fetch_one(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error in fetch_one: {e}")
            return None


# import psycopg2
# import os
# import json
# import sys
# import traceback
# from pathlib import Path

# class Database:
#     def __init__(self):
#         self.connection = None
#         self._config = None  # Cache for configuration

#     def _load_config(self):
#         """Load database configuration with multiple fallback options"""
#         if self._config:
#             return self._config

#         # 1. First try environment variables (for deployment)
#         config = {
#             'dbname': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD'),
#             'host': os.getenv('DB_HOST'),
#             'port': os.getenv('DB_PORT', '5432')  # Default PostgreSQL port
#         }

#         # If all required env vars are set, use them
#         if all(config.values()):
#             self._config = config
#             return config

#         # 2. Try config.json in different locations
#         possible_config_locations = [
#             # For PyInstaller bundled app
#             Path(getattr(sys, '_MEIPASS', '')) / "config.json",
#             # For development
#             Path(__file__).parent / "config.json",
#             # For deployment (same directory as executable)
#             Path(sys.executable).parent / "config.json",
#         ]

#         for config_path in possible_config_locations:
#             if config_path.exists():
#                 try:
#                     with open(config_path, "r") as f:
#                         file_config = json.load(f)
#                     # Merge with any existing config (environment vars take precedence)
#                     config.update({k: v for k, v in file_config.items() if v})
#                     self._config = config
#                     return config
#                 except Exception as e:
#                     print(f"[WARNING] Failed to load config from {config_path}: {e}")
#                     continue

#         # 3. Default values (not recommended for production)
#         if not all(config.values()):
#             config.update({
#                 'dbname': 'papersync',
#                 'user': 'postgres',
#                 'password': 'postgres',
#                 'host': 'localhost',
#                 'port': '5432'
#             })
#             print("[WARNING] Using default database configuration")

#         self._config = config
#         return config

#     def connect(self):
#         """Establish database connection with retry logic"""
#         if self.connection and not self.connection.closed:
#             return self.connection

#         config = self._load_config()
        
#         try:
#             self.connection = psycopg2.connect(
#                 dbname=config['dbname'],
#                 user=config['user'],
#                 password=config['password'],
#                 host=config['host'],
#                 port=config['port'],
#                 connect_timeout=5  # 5 seconds timeout
#             )
#             # Set some connection optimizations
#             self.connection.autocommit = False
#             print(f"[INFO] Connected to PostgreSQL at {config['host']}:{config['port']}")
#             return self.connection
#         except psycopg2.OperationalError as e:
#             print("[ERROR] Could not connect to database:")
#             print(f"  Host: {config['host']}:{config['port']}")
#             print(f"  Database: {config['dbname']}")
#             print(f"  User: {config['user']}")
#             traceback.print_exc()
#             raise  # Re-raise the exception for handling upstream
#         except Exception as e:
#             print("[ERROR] Unexpected database connection error:")
#             traceback.print_exc()
#             raise

#     def get_cursor(self):
#         """Get a database cursor with connection check"""
#         if not self.connection or self.connection.closed:
#             self.connect()
#         return self.connection.cursor()

#     def execute(self, query, params=None, return_result=True):
#         """Execute a query with automatic connection handling"""
#         cursor = None
#         try:
#             cursor = self.get_cursor()
#             cursor.execute(query, params or ())
            
#             if return_result and cursor.description:
#                 return cursor.fetchall()
#             elif return_result:
#                 return None
                
#         except Exception as e:
#             if self.connection:
#                 self.connection.rollback()
#             print(f"[ERROR] Query execution failed: {e}")
#             traceback.print_exc()
#             raise
#         finally:
#             if cursor and not return_result:
#                 cursor.close()

#     def commit(self):
#         """Commit the current transaction"""
#         if self.connection and not self.connection.closed:
#             self.connection.commit()

#     def rollback(self):
#         """Rollback the current transaction"""
#         if self.connection and not self.connection.closed:
#             self.connection.rollback()

#     def close(self):
#         """Close the database connection"""
#         if self.connection and not self.connection.closed:
#             self.connection.close()
#             print("[INFO] Database connection closed")

#     # User-related methods
#     def get_user_first_name(self, username):
#         result = self.execute(
#             "SELECT STAFF_FIRSTNAME FROM STAFF WHERE STAFF_USERNAME = %s",
#             (username,),
#             return_result=True
#         )
#         return result[0][0] if result else None

#     def get_staff_id(self, username):
#         result = self.execute(
#             "SELECT STAFF_ID FROM STAFF WHERE STAFF_USERNAME = %s",
#             (username,),
#             return_result=True
#         )
#         return result[0][0] if result else None

#     def get_staff_name_by_id(self, staff_id):
#         """Get staff full name by ID, returns None if not found"""
#         if staff_id is None:
#             return None
            
#         result = self.execute(
#             "SELECT STAFF_FIRSTNAME, STAFF_LASTNAME FROM STAFF WHERE STAFF_ID = %s",
#             (staff_id,),
#             return_result=True
#         )
        
#         if result:
#             firstname, lastname = result[0]
#             return f"{firstname} {lastname}".strip()
#         return None

#     def __enter__(self):
#         """Support for context manager (with statement)"""
#         self.connect()
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Context manager cleanup"""
#         if exc_type is not None:
#             self.rollback()
#         else:
#             self.commit()
#         self.close()
