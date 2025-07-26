import streamlit as st
import pandas as pd
import os
import oracledb
from testquery import DB_HOST, DB_PORT, DB_SID, DB_USER, DB_PASSWORD

def document_manager_page():
        st.title("📁 Upload and Manage Documents")

        # ✅ Target storage path
        # C:\Users\DELL\Downloads\RailAnalytics\documents
        UPLOAD_FOLDER = r"C:\Users\DELL\Downloads\RailAnalytics\documents"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # --- Upload Section ---
        uploaded_file = st.file_uploader("Choose a document to upload", type=["pdf", "docx", "txt", "xlsx", "jpg", "png"])
        if uploaded_file is not None:
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File uploaded successfully!")

        # --- Search & Manage Section ---
        st.subheader("📄 Search Files")

        search_query = st.text_input("🔍 Search for a file by name")

        if search_query:
            file_list = os.listdir(UPLOAD_FOLDER)
            matched_files = [f for f in file_list if search_query.lower() in f.lower()]

            if matched_files:
                for file_name in matched_files:
                    col1, col2 = st.columns([5, 1])
                    file_path = os.path.join(UPLOAD_FOLDER, file_name)

                    with col1:
                        with open(file_path, "rb") as file:
                            file_data = file.read()
                            st.download_button(
                                label=f"⬇️ Download {file_name}",
                                data=file_data,
                                file_name=file_name,
                                mime="application/octet-stream",
                                key=f"download_{file_name}"
                            )
                    with col2:
                        if st.button("🗑️", key=f"delete_{file_name}"):
                            os.remove(file_path)
                            st.warning(f"🗑️ Deleted '{file_name}'")
                            st.rerun()
            else:
                st.info("No matching files found.")
        else:
            st.markdown("*Upload files above. Use search to view or manage.*")

    
                # --- Excel to Oracle Section ---
                # --- Excel to Oracle Section ---
       
                # --- Excel to Oracle Section ---
        UPLOAD_PATH = r"C:\Users\DELL\Downloads\RailAnalytics\documents"
        os.makedirs(UPLOAD_PATH, exist_ok=True)

        ORACLE_USER = "intern"
        ORACLE_PASSWORD = "inT##2025"
        ORACLE_DSN = "10.3.19.4:1523/traffic"

        st.title("📄 Excel Upload and Auto Table Creation in Oracle")

        uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls", "csv"])

        @st.cache_resource
        def get_oracle_connection():
            return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)

        def infer_sql_types(series):
            if pd.api.types.is_datetime64_any_dtype(series):
                return "DATE"
            try:
                pd.to_numeric(series.dropna(), errors="raise")
                return "NUMBER"
            except:
                pass
            return "VARCHAR2(255)"

        def create_table_from_excel(conn, df, table_name):
            cursor = conn.cursor()
            df.columns = [
                (str(col).strip()
                .replace(" ", "_").replace("-", "_").replace("#", "").replace("@", "")
                .replace("(", "").replace(")", "").upper()[:30]  # truncate to 30 chars
                if isinstance(col, str) and col.strip() else f"COLUMN_{i+1}")
                for i, col in enumerate(df.columns)
            ]
            columns_with_types = ", ".join([f'"{col}" {infer_sql_types(df[col])}' for col in df.columns])
            try:
                cursor.execute(f'DROP TABLE "{table_name}"')
            except:
                pass
            create_sql = f'CREATE TABLE "{table_name}" ({columns_with_types})'
            try:
                cursor.execute(create_sql)
                conn.commit()
                st.success(f"✅ Table created in Oracle")
            except Exception as e:
                st.error(f"❌ Failed to create table: {e}")
                return False
                # st.error(f"Table already exist")
                # return False
            return True

        def insert_data_to_table(conn, df, table_name):
            cursor = conn.cursor()
            columns = ", ".join([f'"{col}"' for col in df.columns])
            placeholders = ", ".join([f":{i+1}" for i in range(len(df.columns))])
            insert_sql = f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({placeholders})"
            for col in df.columns:
                inferred_type = infer_sql_types(df[col])
                if inferred_type in ["NUMBER", "FLOAT"]:
                    df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False)
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif inferred_type == "DATE":
                    try:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df[col], unit="D")
                        else:
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                        df[col] = df[col].dt.date
                    except Exception as e:
                        st.warning(f"⚠️ Failed to convert {col} to date: {e}")
                elif inferred_type == "VARCHAR2(255)":
                    df[col] = df[col].astype(str).str.strip()
            df = df.replace(r'^\s*$', None, regex=True)
            df = df.astype(object).where(pd.notnull(df), None)
            try:
                batch_size = 5000
                total_rows = len(df)
                for start in range(0, total_rows, batch_size):
                    end = start + batch_size
                    batch = df.iloc[start:end].values.tolist()
                    cursor.executemany(insert_sql, batch)
                    conn.commit()
                st.success(f"✅ Inserted {total_rows} rows into '{table_name}'")
            except Exception as e:
                conn.rollback()
                st.error(f"❌ Data insertion failed: {str(e)}")

        def get_table_columns(conn, table_name):
            cursor = conn.cursor()
            cursor.execute(f"SELECT column_name FROM user_tab_columns WHERE table_name = '{table_name.upper()}' ORDER BY column_id")
            return [row[0] for row in cursor.fetchall()]

        def fetch_user_tables(conn):
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM EXCEL ORDER BY created_on DESC")
            return [row[0] for row in cursor.fetchall()]

        def log_uploaded_table(conn, table_name):
            cursor = conn.cursor()
            username = st.session_state.get("username", "system")  # Current user who uploaded/modified

            # Check if table already exists in log
            cursor.execute("SELECT COUNT(*) FROM EXCEL WHERE table_name = :1", [table_name])
            exists = cursor.fetchone()[0]

            if exists:
                # Table already logged — update modified info
                cursor.execute("""
                    UPDATE EXCEL
                    SET modified_by = :1,
                        modified_on = SYSTIMESTAMP
                    WHERE table_name = :2
                """, [username, table_name])
            else:
                # New table log — set created_by and modified_by initially
                cursor.execute("""
                    INSERT INTO EXCEL (table_name, created_by, created_on, modified_by, modified_on)
                    VALUES (:1, :2, SYSTIMESTAMP, :3, SYSTIMESTAMP)
                """, [table_name, username, username])

            conn.commit()


        if uploaded_file:
            saved_path = os.path.join(UPLOAD_PATH, uploaded_file.name)
            with open(saved_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File saved: {saved_path}")

            try:
                if saved_path.lower().endswith(".xls"):
                    import pyexcel as pe
                    records = pe.get_records(file_name=saved_path)
                    df = pd.DataFrame(records)
                    new_path = saved_path.replace(".xls", ".xlsx")
                    df.to_excel(new_path, index=False)
                    saved_path = new_path
                    st.warning("⚠ Converted .xls to .xlsx using pyexcel.")
                if saved_path.lower().endswith(".xlsx"):
                    df = pd.read_excel(saved_path, engine="openpyxl")
                elif saved_path.lower().endswith(".csv"):
                    df = pd.read_csv(saved_path)
                else:
                    st.error("❌ Unsupported file format. Please upload .xls, .xlsx, or .csv")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Failed to read file: {e}")
                return False

            df.dropna(axis=1, how='all', inplace=True)
            default_name = os.path.splitext(uploaded_file.name)[0].upper()
            table_name = st.text_input("Enter new Oracle table name", value=default_name)

            conn = get_oracle_connection()

            st.dataframe(df.head())
            operation = st.radio("Choose Operation", ["Create New Table & Upload", "Append to Existing Table"])

            if operation == "Create New Table & Upload":
                if st.button("Create Table & Upload Data"):
                    if create_table_from_excel(conn, df, table_name):
                        log_uploaded_table(conn, table_name)
                        insert_data_to_table(conn, df, table_name)

            elif operation == "Append to Existing Table":
                append_mode = st.selectbox("Select Append Mode", ["Manually Insert Row", "Manually Insert Column"])

                if append_mode == "Manually Insert Row":
                    existing_cols = get_table_columns(conn, table_name)

                    if not existing_cols:
                        st.warning("⚠ Cannot insert row: Table exists but has no columns. Please re-upload or verify table schema.")
                    else:
                        st.subheader("🧾 Enter values to insert in new row")
                        new_row = {}
                        for col in existing_cols:
                            new_row[col] = st.text_input(f"Enter value for '{col}'", key=f"input_{col}")

                    if st.button("➕ Append New Row"):
                        row_to_insert = [new_row[col] if new_row[col] != '' else None for col in existing_cols]
                        try:
                            cursor = conn.cursor()
                            placeholders = ", ".join([f":{i+1}" for i in range(len(existing_cols))])
                            insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f'"{col}"' for col in existing_cols])}) VALUES ({placeholders})'
                            cursor.execute(insert_sql, row_to_insert)
                            conn.commit()

                            # Log modification after row insert
                            log_uploaded_table(conn, table_name)

                            if saved_path.lower().endswith(".csv"):
                                excel_df = pd.read_csv(saved_path)
                            else:
                                excel_df = pd.read_excel(saved_path, engine="openpyxl")

                            new_row_df = pd.DataFrame([row_to_insert], columns=existing_cols)
                            updated_excel = pd.concat([excel_df, new_row_df], ignore_index=True)
                            if saved_path.lower().endswith(".csv"):
                                updated_excel.to_csv(saved_path, index=False)
                            else:
                                updated_excel.to_excel(saved_path, index=False)

                            st.write("📄 Last 5 rows of updated Excel file:")
                            st.dataframe(updated_excel.tail())

                            st.success("✅ Row inserted into Oracle and Excel file.")
                        except Exception as e:
                            st.error(f"❌ Failed to insert: {e}")

                    elif append_mode == "Manually Insert Column":
                        existing_cols = get_table_columns(conn, table_name)
                        new_col_name = st.text_input("Enter new column name")
                        new_col_type = st.selectbox("Select data type", ["VARCHAR2(255)", "NUMBER", "DATE"])

                        if st.button("➕ Add New Column") and new_col_name:
                            try:
                                cursor = conn.cursor()
                                cursor.execute(f'ALTER TABLE "{table_name}" ADD ("{new_col_name}" {new_col_type})')
                                conn.commit()

                                # Log modification after column insert
                                log_uploaded_table(conn, table_name)

                                st.success(f"✅ Column '{new_col_name}' added to Oracle table.")

                                # Update Excel/CSV file
                                if saved_path.lower().endswith(".csv"):
                                    excel_df = pd.read_csv(saved_path)
                                    excel_df[new_col_name] = None  # Add new column
                                    excel_df.to_csv(saved_path, index=False)
                                else:
                                    excel_df = pd.read_excel(saved_path, engine="openpyxl")
                                    excel_df[new_col_name] = None
                                    excel_df.to_excel(saved_path, index=False)

                                st.success("✅ Column also added to Excel file.")
                            except Exception as e:
                                st.error(f"❌ Failed to add column: {e}")


        st.header("📜 View Your Uploaded Oracle Tables")
        try:
            conn = get_oracle_connection()
            user_tables = fetch_user_tables(conn)
            if user_tables:
                selected_table = st.selectbox("Select a table to view:", user_tables)
                if st.button("🔍 View Table"):
                    df = pd.read_sql(f'SELECT * FROM "{selected_table}"', conn)
                    st.dataframe(df)
            else:
                st.info("No uploaded tables found.")
        except Exception as e:
            st.error(f"❌ Oracle connection failed: {e}")

            