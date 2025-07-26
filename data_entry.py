import streamlit as st
import oracledb
import pandas as pd
from datetime import datetime

# --- Oracle Instant Client Configuration ---
INSTANT_CLIENT_PATH = r"D:\Utils\instantclient-basic-windows.x64-23.8.0.25.04\instantclient_23_8"

# --- Database Connection Parameters ---
DB_USER = "intern"
DB_PASSWORD = "inT##2025"
DB_HOST = "10.3.19.4"
DB_PORT = 1523
DB_SID = "traffic"
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SID}"

# Initialize connection
@st.cache_resource
def init_connection():
    try:
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DSN
        )
        return connection
    except Exception as e:
        st.error(f"Error connecting to Oracle DB: {e}")
        return None

# CRUD Operations
def main():
    st.title("Oracle Database CRUD Operations")
    conn = init_connection()
    if not conn:
        return
    
    TABLE_NAME = "DATA_STORE"

    operation = st.sidebar.selectbox(
        "Operation",
        ["View Data", "Insert Data", "Update Data", "Delete Data", "Search Data"]
    )
    
    # View Data
    if operation == "View Data":
        st.header("View Stored Data")
        try:
            query = f"SELECT id, category, data_key, last_updated FROM {TABLE_NAME} ORDER BY last_updated DESC"
            df = pd.read_sql(query, conn)
            st.dataframe(df)
            
            if st.checkbox("Show Full Data"):
                full_query = f"SELECT * FROM {TABLE_NAME}"
                full_df = pd.read_sql(full_query, conn)
                st.dataframe(full_df)
                
        except Exception as e:
            st.error(f"Error viewing data: {e}")
    
    # Insert Data
    elif operation == "Insert Data":
        st.header("Insert New Data")
        with st.form("insert_form"):
            category = st.text_input("Category*", placeholder="e.g., user_preferences")
            data_key = st.text_input("Unique Key*", placeholder="e.g., user123_config")
            data_value = st.text_area("Data Value (JSON/Text)*", placeholder='{"theme": "dark", "language": "en"}')
            user = st.text_input("Your Name", placeholder="Optional")
            
            submitted = st.form_submit_button("Insert Data")
            if submitted:
                if not category or not data_key or not data_value:
                    st.warning("Please fill all required fields (*)")
                else:
                    try:
                        cursor = conn.cursor()
                        # Ensure sequence exists before insert
                        seq_check = f"""
                            SELECT sequence_name FROM user_sequences WHERE sequence_name = UPPER('{TABLE_NAME}_SEQ')
                        """
                        cursor.execute(seq_check)
                        if not cursor.fetchone():
                            try:
                                cursor.execute(f"CREATE SEQUENCE {TABLE_NAME}_SEQ START WITH 1 INCREMENT BY 1 NOCACHE")
                                conn.commit()  # Ensure the sequence is committed
                            except Exception as se:
                                pass  # Suppress debug messages
                        
                        query = f"""
                            INSERT INTO {TABLE_NAME} (
                                id, category, data_key, data_value, user_modified, last_updated
                            ) VALUES (
                                {TABLE_NAME}_SEQ.NEXTVAL, :cat, :dkey, :dval, :usr, SYSTIMESTAMP
                            )
                        """
                        cursor.execute(query, {
                            "cat": category,
                            "dkey": data_key,
                            "dval": data_value,
                            "usr": user if user else "system"
                        })
                        conn.commit()
                        st.success("✅ Data inserted successfully!")
                        
                    except oracledb.DatabaseError as e:
                        conn.rollback()
                        error_obj, = e.args
                        if error_obj.code == 1:  # Unique constraint violation
                            st.error("❌ Error: This key already exists. Please use a different key.")
                        else:
                            st.error(f"❌ Database error: {error_obj.message}")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error inserting data: {e}")
                    finally:
                        cursor.close()

    # Update Data
    elif operation == "Update Data":
        st.header("Update Existing Data")
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, data_key FROM {TABLE_NAME} ORDER BY id")
            records = cursor.fetchall()
            cursor.close()
            
            if not records:
                st.warning("No records found to update.")
            else:
                record_options = {f"{rec[0]} - {rec[1]}": rec[0] for rec in records}
                selected_display = st.selectbox("Select record to update", list(record_options.keys()))
                selected_id = record_options[selected_display]
                
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT category, data_key, data_value, user_modified 
                    FROM {TABLE_NAME} 
                    WHERE id = :id
                """, id=selected_id)
                current_data = cursor.fetchone()
                cursor.close()
                
                if current_data:
                    with st.form("update_form"):
                        st.write(f"Updating record ID: {selected_id}")
                        category = st.text_input("Category*", value=current_data[0])
                        new_key = st.text_input("New Key*", value=current_data[1])
                        data_value = st.text_area("New Value*", value=current_data[2])
                        user = st.text_input("Updated By", value=current_data[3] if current_data[3] else "system")
                        
                        submitted = st.form_submit_button("Update Record")
                        if submitted:
                            if not category or not new_key or not data_value:
                                st.warning("Please fill all required fields (*)")
                            else:
                                try:
                                    cursor = conn.cursor()
                                    query = f"""
                                        UPDATE {TABLE_NAME}
                                        SET 
                                            category = :cat,
                                            data_key = :dkey,
                                            data_value = :dval,
                                            user_modified = :usr,
                                            last_updated = SYSTIMESTAMP
                                        WHERE id = :id
                                    """
                                    cursor.execute(query, {
                                        "cat": category,
                                        "dkey": new_key,
                                        "dval": data_value,
                                        "usr": user if user else "system",
                                        "id": selected_id
                                    })
                                    conn.commit()
                                    st.success("✅ Data updated successfully!")
                                except oracledb.DatabaseError as e:
                                    conn.rollback()
                                    error_obj, = e.args
                                    if error_obj.code == 1:
                                        st.error("❌ Error: This key already exists.")
                                    else:
                                        st.error(f"❌ Database error: {error_obj.message}")
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ Error updating data: {e}")
                                finally:
                                    cursor.close()
                else:
                    st.warning("Selected record not found.")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Delete Data
    elif operation == "Delete Data":
        st.header("Delete Data")
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, data_key FROM {TABLE_NAME} ORDER BY id")
            records = cursor.fetchall()
            cursor.close()
            
            if not records:
                st.warning("No records found to delete.")
            else:
                record_options = {f"{rec[0]} - {rec[1]}": rec[0] for rec in records}
                selected_display = st.selectbox("Select record to delete", list(record_options.keys()))
                selected_id = record_options[selected_display]
                
                st.warning(f"You are about to delete record ID: {selected_id}")
                if st.button("Confirm Deletion", type="primary"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"""
                            SELECT * FROM {TABLE_NAME} WHERE id = :id
                        """, id=selected_id)
                        deleted_record = cursor.fetchone()
                        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = :id", id=selected_id)
                        conn.commit()
                        if deleted_record:
                            st.success(f"✅ Record deleted successfully!")
                            st.json({
                                "id": deleted_record[0],
                                "category": deleted_record[1],
                                "key": deleted_record[2],
                                "last_updated": str(deleted_record[5])
                            })
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ Error deleting record: {e}")
                    finally:
                        cursor.close()
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Search Data
    elif operation == "Search Data":
        st.header("Search Data")
        with st.form("search_form"):
            search_term = st.text_input("Search term")
            search_by = st.radio("Search by", ["Category", "Key", "Content"])
            
            submitted = st.form_submit_button("Search")
            if submitted and search_term:
                try:
                    cursor = conn.cursor()
                    if search_by == "Category":
                        query = f"""
                            SELECT id, category, data_key, last_updated 
                            FROM {TABLE_NAME} 
                            WHERE UPPER(category) LIKE UPPER(:term)
                            ORDER BY last_updated DESC
                        """
                    elif search_by == "Key":
                        query = f"""
                            SELECT id, category, data_key, last_updated 
                            FROM {TABLE_NAME} 
                            WHERE UPPER(data_key) LIKE UPPER(:term)
                            ORDER BY last_updated DESC
                        """
                    else:
                        query = f"""
                            SELECT id, category, data_key, last_updated 
                            FROM {TABLE_NAME} 
                            WHERE UPPER(data_value) LIKE UPPER(:term)
                            ORDER BY last_updated DESC
                        """
                    
                    cursor.execute(query, term=f"%{search_term}%")
                    results = cursor.fetchall()
                    
                    if results:
                        df = pd.DataFrame(results, columns=["ID", "Category", "Key", "Last Updated"])
                        st.dataframe(df)
                        
                        if st.checkbox("Show matching content"):
                            for row in results:
                                cursor.execute(f"""
                                    SELECT data_value FROM {TABLE_NAME} WHERE id = :id
                                """, id=row[0])
                                content = cursor.fetchone()[0]
                                with st.expander(f"Content for {row[2]}"):
                                    st.code(content)
                    else:
                        st.info("No results found")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
                finally:
                    cursor.close()

if __name__ == "__main__":
    main()
