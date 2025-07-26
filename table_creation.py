import oracledb
from datetime import datetime

# --- Oracle Instant Client Configuration ---
INSTANT_CLIENT_PATH = r"C:\Users\PC\Downloads\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.19.4"
DB_PORT = 1523
DB_SID = "traffic"
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# --- Table/Schema ---
TARGET_SCHEMA = "FOISGOODS"

def create_table():
    # Initialize Oracle client (if needed)
    oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
    
    try:
        # Connect to Oracle (replace with your credentials)
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DSN
        )
        
        cursor = connection.cursor()
        table_name = "DATA_STORE"
        # Only create table and sequence if they do not exist
        cursor.execute(f"""
            SELECT table_name FROM user_tables WHERE table_name = UPPER('{table_name}')
        """)
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE TABLE {table_name} (
                    id NUMBER PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                    category VARCHAR2(100),
                    data_key VARCHAR2(100) UNIQUE,
                    data_value CLOB,
                    last_updated TIMESTAMP,
                    user_modified VARCHAR2(50)
                )
            """)
            try:
                cursor.execute(f"CREATE SEQUENCE {table_name}_SEQ START WITH 1 INCREMENT BY 1 NOCACHE")
            except Exception:
                pass
            cursor.execute(f"""
                CREATE INDEX idx_{table_name}_category ON {table_name}(category)
            """)
            cursor.execute(f"""
                CREATE INDEX idx_{table_name}_data_key ON {table_name}(data_key)
            """)
            connection.commit()
            print(f"Table {table_name} created successfully!")
        else:
            print(f"Table {table_name} already exists")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    create_table()