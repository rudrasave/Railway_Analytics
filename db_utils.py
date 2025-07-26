import streamlit as st
import oracledb
import os

# --- Oracle Instant Client Configuration ---
INSTANT_CLIENT_PATH = r"C:\Users\Abishek\Downloads\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.19.4"
DB_PORT = 1523
DB_SID = "traffic"
TARGET_SCHEMA = "FOISGOODS"
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# Initialize Oracle thick mode
try:
    if not oracledb.init_oracle_client():
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
except Exception as e:
    print(f"Failed to initialize Oracle Client: {str(e)}")
    if 'streamlit' in globals():
        st.error(f"""
        ❌ Failed to initialize Oracle Client libraries. 
        Please ensure Oracle Instant Client is installed at: {INSTANT_CLIENT_PATH}
        Error: {str(e)}
        """)

def get_db_connection():
    """Create and return a database connection with proper error handling"""
    try:
        return oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DSN,
            config_dir=INSTANT_CLIENT_PATH,  # Add config directory
            thick_mode=True  # Explicitly enable thick mode
        )
    except oracledb.Error as e:
        error_msg = str(e)
        if "DPY-6005" in error_msg:
            msg = """
            ❌ Failed to connect to the database. 
            Please check:
            1. Database server is running and accessible
            2. Network connection is stable
            3. Credentials are correct
            """
        elif "DPY-3010" in error_msg:
            msg = """
            ❌ Oracle Client version mismatch. 
            Please ensure you have the correct version of Oracle Instant Client installed.
            Download from: https://www.oracle.com/database/technologies/instant-client/downloads.html
            """
        else:
            msg = f"❌ Database connection error: {error_msg}"
            
        print(msg)
        if 'streamlit' in globals():
            st.error(msg)
        raise

# Context manager for database connections
class DatabaseConnection:
    def __enter__(self):
        self.conn = get_db_connection()
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'conn'):
            self.conn.close()
