import oracledb
import pandas as pd # Import the pandas library
import sys
import os

# --- Oracle Instant Client Configuration ---
# IMPORTANT: Set this to the EXACT path where you extracted Instant Client.
# This path must contain the .dll files (e.g., oci.dll).
INSTANT_CLIENT_PATH = r"C:\Users\DELL\Desktop\Intership\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.9.4"
DB_PORT = 1523
DB_SID = "traffic"

# --- Table Details ---
TARGET_SCHEMA = "FOISGOODS"
TARGET_TABLE = "UPI_29052025"

# --- CSV Output File ---
OUTPUT_CSV_FILENAME = f"{TARGET_TABLE}_data.csv" # e.g., WR_TRAIN_LIST_data.csv

# Construct the DSN (Data Source Name) string for SID connection
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# --- Initialize Oracle Client for Thick Mode ---
print("Initializing Oracle Client for Thick Mode...")
try:
    oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
    print(f"Oracle Client initialized successfully from: {INSTANT_CLIENT_PATH}")
except oracledb.Error as e:
    error_obj = e.args[0]
    print(f"\n--- Oracle Client Initialization Error ---")
    print(f"Error Message: {error_obj.message}")
    print(f"Please ensure Instant Client is installed correctly at:")
    print(f"  {INSTANT_CLIENT_PATH}")
    print(f"And that the path contains the necessary DLLs (like oci.dll).")
    sys.exit(1)

print(f"\nAttempting to connect to Oracle Database: {DSN} as user: {DB_USER}")
print("-" * 30)

# --- Connection and Data Pull Logic ---
connection = None
cursor = None

try:
    print("Establishing database connection...")
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN)
    print("Successfully connected to the Oracle Database!")

    # Define the SQL query to select all data from your table
    # Using the full schema.table_name to be explicit
    query = f"SELECT * FROM {TARGET_SCHEMA}.{TARGET_TABLE}"

    print(f"\nExecuting query to fetch data from {TARGET_SCHEMA}.{TARGET_TABLE}...")
    cursor = connection.cursor()
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Get column names from the cursor description
    column_names = [col[0] for col in cursor.description]

    if not rows:
        print(f"No data found in table {TARGET_SCHEMA}.{TARGET_TABLE}.")
    else:
        print(f"Fetched {len(rows)} rows.")

        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)

        # Save DataFrame to CSV
        df.to_csv(OUTPUT_CSV_FILENAME, index=False, encoding='utf-8')
        print(f"\nData successfully saved to '{OUTPUT_CSV_FILENAME}'")

except oracledb.Error as e:
    error_obj = e.args[0]
    print(f"\n--- Database Error Occurred ---")
    print(f"Oracle Error Code: {error_obj.code}")
    print(f"Error Message: {error_obj.message}")
    if hasattr(error_obj, 'sqlstate'):
        print(f"SQLSTATE: {error_obj.sqlstate}")
    print(f"Please ensure '{TARGET_SCHEMA}.{TARGET_TABLE}' exists and user '{DB_USER}' has SELECT privileges on it.")
    print("-" * 30)

except Exception as e:
    print(f"\n--- An unexpected Python error occurred ---")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("Please check your Python code, especially pandas installation.")
    print("-" * 30)

finally:
    print("\n--- Closing connections ---")
    if cursor:
        cursor.close()
        print("Cursor closed.")
    if connection:
        connection.close()
        print("Connection closed.")