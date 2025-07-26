import oracledb
import sys

# --- Oracle Instant Client Configuration ---
INSTANT_CLIENT_PATH = r"C:\Users\DELL\Desktop\Intership\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.19.4"
DB_PORT = 1523
DB_SID = "traffic"

# --- Table Details ---
TARGET_SCHEMA = "FOISGOODS"
TARGET_TABLE = "carr_apmt_excl_adv_20_21"

# Construct the DSN (Data Source Name) string for SID connection
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# --- Initialize Oracle Client for Thick Mode ---
try:
    oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
except oracledb.Error as e:
    print(f"Oracle Client Initialization Error: {e}")
    sys.exit(1)

# --- Query Logic ---
connection = None
cursor = None

try:
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN)
    cursor = connection.cursor()
    query = f"""
        SELECT SUM(WR) AS SUM_DIFF
        FROM {TARGET_SCHEMA}.{TARGET_TABLE}
        WHERE ZONE_FRM = 'WR'
      
    """
    cursor.execute(query)
    result = cursor.fetchone()
    sum_diff = result[0] if result else None
    print(f"Value : {sum_diff}")
except oracledb.Error as e:
    print(f"Database Error: {e}")
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
