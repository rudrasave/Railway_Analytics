import oracledb
import pandas as pd
import streamlit as st
from datetime import datetime
import re
from io import BytesIO
import plotly.express as px

# --- Oracle Instant Client Configuration ---
INSTANT_CLIENT_PATH = r"C:\Users\Craig Michael Dsouza\Downloads\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.9.4"
DB_PORT = 1523
DB_SID = "traffic"

# --- Constants ---
TARGET_SCHEMA = "FOISGOODS"
DATE_COLUMN = "YYMM"
ZONE_COLUMN = "ZONE_FRM"
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# Financial year months (April to March)
FINANCIAL_MONTHS = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March"
]

# Map financial years to table suffixes (e.g., 2024-2025 -> 24_25)
FINANCIAL_YEARS = {
    "2024-2025": "24_25",
    "2023-2024": "23_24",
    "2022-2023": "22_23",
    "2021-2022": "21_22",
    "2020-2021": "20_21",
    "2019-2020": "19_20",
    "2018-2019": "18_19",
    "2017-2018": "17_18"
}

@st.cache_resource
def init_oracle_client():
    try:
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
        return True
    except oracledb.Error as e:
        st.error(f"Oracle Client Error: {e}")
        return False

def get_table_name(financial_year):
    """Get table name based on financial year selection."""
    if financial_year in FINANCIAL_YEARS:
        return f"CARR_APMT_EXCL_ADV_{FINANCIAL_YEARS[financial_year]}"
    return None

@st.cache_data(ttl=3600, show_spinner="Loading table data...")
def load_data(table_name):
    """Optimized data loading that fetches all rows while being memory efficient."""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN) as conn:
            # First get column names
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TARGET_SCHEMA}.{table_name} WHERE ROWNUM = 0")
            cols = [col[0] for col in cursor.description]
            
            # Use cursor to fetch data in batches
            cursor.execute(f"SELECT * FROM {TARGET_SCHEMA}.{table_name}")
            
            # Initialize empty DataFrame with correct columns
            df = pd.DataFrame(columns=cols)
            
            # Fetch data in chunks to be memory efficient
            chunk_size = 10000
            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break
                temp_df = pd.DataFrame(rows, columns=cols)
                df = pd.concat([df, temp_df], ignore_index=True)
            
            # Convert date column if present
            if DATE_COLUMN in df.columns:
                df['temp_date'] = pd.to_datetime(
                    df[DATE_COLUMN].astype(str), 
                    format='%Y%m', 
                    errors='coerce'
                )
                df = df.dropna(subset=['temp_date'])
                # Add financial year column (April-March)
                df['financial_year'] = df['temp_date'].apply(
                    lambda x: f"{x.year}-{x.year+1}" if x.month >=4 else f"{x.year-1}-{x.year}"
                )
                # Add financial month name
                df['financial_month'] = df['temp_date'].dt.month.apply(
                    lambda x: FINANCIAL_MONTHS[x-4] if x >=4 else FINANCIAL_MONTHS[x+8]
                )
            
            return df
    except Exception as e:
        st.error(f"Data load failed: {e}")
        return pd.DataFrame()

def filter_data(df, start_month=None, end_month=None, zone=None):
    """Filter data by month range (April-March cycle) and zone."""
    if df.empty:
        return df

    filtered_df = df.copy()
    
    if start_month and end_month and start_month != "All" and end_month != "All":
        start_idx = FINANCIAL_MONTHS.index(start_month)
        end_idx = FINANCIAL_MONTHS.index(end_month)
        
        if start_idx <= end_idx:
            # Normal range (e.g., April-September)
            valid_months = FINANCIAL_MONTHS[start_idx:end_idx+1]
        else:
            # Wraparound range (e.g., November-February)
            valid_months = FINANCIAL_MONTHS[start_idx:] + FINANCIAL_MONTHS[:end_idx+1]
        
        filtered_df = filtered_df[filtered_df['financial_month'].isin(valid_months)]
    
    if zone and zone != "All" and ZONE_COLUMN in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[ZONE_COLUMN] == zone]

    return filtered_df.drop(['temp_date', 'financial_year', 'financial_month'], axis=1, errors='ignore')

def main():
    st.set_page_config("Oracle Excel Exporter", layout="wide")
    st.title("📦 Railway Analytics Data Exporter (Financial Year)")

    # Oracle Init
    if not init_oracle_client():
        st.stop()

    # Sidebar - Financial Year Selection
    with st.sidebar:
        st.header("1. Select Financial Year")
        selected_fy = st.selectbox(
            "Financial Year",
            options=list(FINANCIAL_YEARS.keys()),
            index=0
        )
        
        # Automatically determine table name
        table_name = get_table_name(selected_fy)
        
        # Load data with progress indication
        with st.spinner(f"Loading {table_name} (this may take a while for large tables)..."):
            df = load_data(table_name)
            
        if df.empty:
            st.error("No data found for selected financial year.")
            st.stop()
            
        st.header("2. Filter Options")
        
        # Month range selection
        st.subheader("Month Range (April-March)")
        col1, col2 = st.columns(2)
        with col1:
            start_month = st.selectbox(
                "From",
                options=["All"] + FINANCIAL_MONTHS,
                index=0
            )
        with col2:
            end_month = st.selectbox(
                "To",
                options=["All"] + FINANCIAL_MONTHS,
                index=0 if start_month == "All" else FINANCIAL_MONTHS.index(start_month)
            )
        
        # Zone selection
        zone_options = ["All"]
        if ZONE_COLUMN in df.columns:
            zone_options.extend(sorted(df[ZONE_COLUMN].dropna().unique()))
        
        selected_zone = st.selectbox("Zone", zone_options)
        
        st.markdown("### Actions")
        preview = st.button("🔍 Preview")
        download = st.button("📥 Export to Excel")

    # Filter data
    filtered_df = filter_data(df, start_month, end_month, selected_zone)

    # Tabs
    tab1, tab2 = st.tabs(["📊 Data Preview", "📈 Charts"])

    with tab1:
        if preview:
            st.subheader("Filtered Preview")
            if filtered_df.empty:
                st.warning("No matching records.")
            else:
                st.success(f"{len(filtered_df)} rows found (showing first 1000).")
                st.dataframe(filtered_df.head(1000))

    with tab2:
        if 'financial_month' in df.columns:
            st.subheader("📅 Monthly Distribution")
            month_count = df['financial_month'].value_counts()
            month_count = month_count.reindex(FINANCIAL_MONTHS)  # Ensure correct order
            st.bar_chart(month_count)

        if ZONE_COLUMN in df.columns:
            st.subheader("🗺️ Records by Zone")
            zone_count = df[ZONE_COLUMN].value_counts()
            st.bar_chart(zone_count)

    # Excel Export
    if download:
        if filtered_df.empty:
            st.warning("No data to export.")
        else:
            output = BytesIO()
            with st.spinner("Preparing Excel file..."):
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, index=False)

            # Create filename
            parts = [table_name]
            
            if start_month != "All" and end_month != "All":
                month_part = f"{start_month[:3]}-{end_month[:3]}"
                parts.append(month_part)
            
            if selected_zone != "All":
                parts.append(selected_zone.replace(" ", "_"))
            
            filename = "_".join(parts) + ".xlsx"

            st.download_button(
                "📥 Download Excel File",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success(f"File ready: {filename}")

if __name__ == "__main__":
    main()