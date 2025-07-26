import oracledb
import sys

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
TARGET_SCHEMA = "FOISGOODS" # The schema owning the table
TARGET_TABLE = "WR_TRAIN_LIST" # The table name

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

# --- Connection and Query Logic ---
connection = None
cursor = None

try:
    print("Establishing database connection...")
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN)
    print("Successfully connected to the Oracle Database!")

    cursor = connection.cursor()

    # --- 1. Get Number of Rows ---
    print(f"\n--- Getting row count for {TARGET_SCHEMA}.{TARGET_TABLE} ---")
    count_query = f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{TARGET_TABLE}"
    try:
        cursor.execute(count_query)
        row_count = cursor.fetchone()[0]
        print(f"Number of rows in {TARGET_SCHEMA}.{TARGET_TABLE}: {row_count}")
    except oracledb.Error as e:
        print(f"Error getting row count: {e.args[0].message}")
        print(f"Please ensure '{TARGET_SCHEMA}.{TARGET_TABLE}' exists and user '{DB_USER}' has SELECT privileges.")
        row_count = "N/A (Error)"


    # --- 2. Get Column Names and Data Types ---
    print(f"\n--- Getting column details for {TARGET_SCHEMA}.{TARGET_TABLE} ---")
    columns_query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, DATA_SCALE, NULLABLE
        FROM ALL_TAB_COLUMNS
        WHERE OWNER = :schema_name AND TABLE_NAME = :table_name
        ORDER BY COLUMN_ID
    """
    try:
        cursor.execute(columns_query, schema_name=TARGET_SCHEMA.upper(), table_name=TARGET_TABLE.upper())

        column_details = cursor.fetchall()

        if column_details:
            print(f"Column Name          Data Type")
            print(f"-------------------- --------------------")
            for col in column_details:
                col_name = col[0]
                data_type = col[1]
                data_length = col[2]
                data_precision = col[3]
                data_scale = col[4]
                nullable = "NULL" if col[5] == 'Y' else "NOT NULL"

                # Format data type for better readability, especially for numbers and strings
                if data_type in ('NUMBER', 'FLOAT'):
                    if data_precision is not None and data_scale is not None:
                        display_type = f"{data_type}({data_precision},{data_scale})"
                    elif data_precision is not None:
                         display_type = f"{data_type}({data_precision})"
                    else:
                        display_type = data_type
                elif data_type in ('VARCHAR2', 'NVARCHAR2', 'CHAR', 'NCHAR', 'RAW'):
                    display_type = f"{data_type}({data_length})"
                else:
                    display_type = data_type

                print(f"{col_name:<20} {display_type:<20}")
        else:
            print(f"No column details found for {TARGET_SCHEMA}.{TARGET_TABLE}.")
            print("Possible reasons:")
            print(f"  - Table '{TARGET_TABLE}' does not exist in schema '{TARGET_SCHEMA}'.")
            print("  - The 'intern' user does not have privileges to see table columns in ALL_TAB_COLUMNS.")

    except oracledb.Error as e:
        print(f"Error getting column details: {e.args[0].message}")
        print(f"Please ensure '{TARGET_SCHEMA}.{TARGET_TABLE}' exists and user '{DB_USER}' has SELECT privileges on ALL_TAB_COLUMNS.")


except oracledb.Error as e:
    # General database error for connection or overall process
    error_obj = e.args[0]
    print(f"\n--- General Database Error Occurred ---")
    print(f"Oracle Error Code: {error_obj.code}")
    print(f"Error Message: {error_obj.message}")
    if hasattr(error_obj, 'sqlstate'):
        print(f"SQLSTATE: {error_obj.sqlstate}")
    print("Please check your database credentials, network connectivity, and user privileges.")
    print("-" * 30)

except Exception as e:
    # Catch any other unexpected Python errors
    print(f"\n--- An unexpected Python error occurred ---")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("Please check your Python code for syntax errors or logical issues.")
    print("-" * 30)

finally:
    print("\n--- Closing connections ---")
    if cursor:
        cursor.close()
        print("Cursor closed.")
    if connection:
        connection.close()
        print("Connection closed.")