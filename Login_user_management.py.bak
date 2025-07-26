import streamlit as st
import pandas as pd
import oracledb
import hashlib
from email.message import EmailMessage
import smtplib
import random
from testquery import DB_HOST, DB_PORT, DB_SID, DB_USER, DB_PASSWORD

# Session state defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ------------------- LOGIN / SIGNUP -------------------    
def login_user(username, password):
    hashed = hash_password(password)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = :1 AND password_hash = :2 AND is_active='Y'", (username, hashed))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def signup_user(username, password, role, email):
    try:
        hashed = hash_password(password)
        conn = create_connection()
        cursor = conn.cursor()

        # Check for existing username
        cursor.execute("SELECT 1 FROM users WHERE username = :1", (username,))
        if cursor.fetchone():
            return "Username already exists."

        # Insert user with email
        cursor.execute("""
            INSERT INTO users (ID, USERNAME, PASSWORD_HASH, ROLE, EMAIL, IS_ACTIVE, LAST_UPDATED)
            VALUES (seq_users_id.NEXTVAL, :1, :2, :3, :4, 'Y', SYSTIMESTAMP)
        """, (username, hashed, role, email))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return f"Signup failed: {e}"


# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DB connection
def create_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DSN)


# --- pwermission ---
def get_all_employees():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE role='employee'")
    employees = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return employees

def set_employee_access(username, pages):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_permissions WHERE username = :1", [username])
    for page in pages:
        cursor.execute("INSERT INTO user_permissions (username, page_name) VALUES (:1, :2)", (username, page))
    conn.commit()
    cursor.close()
    conn.close()

def get_employee_permissions(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT page_name FROM user_permissions WHERE username = :1", [username])
    permissions = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return permissions



# Login/Signup UI
def login_signup_screen():


    # Set page config
    st.set_page_config(page_title="Indian Railways Login", layout="centered")

    # Apply custom CSS
    st.markdown(r"""
        <style>
        .stApp {
            background-color: #00214d;
        }

        .login-title {
            font-size: 30px;
            font-weight: bold;
            color: white;
            margin-top: 15px;
            margin-bottom: 30px;
        }
        .login-input {
            width: 100%;
            padding: 15px 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 18px;
        }
        .login-button {
            background-color: #003366;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            margin-top: 15px;
            cursor: pointer;
            font-weight: bold;
            font-size: 18px;
        }
        .footer {
            margin-top: 30px;
            font-size: 18px;
            color: white;
        }
          
        .custom-checkbox {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 16px;
        margin-top: 8px;
        color: white;
        }
        /* Force white color on the expander label text */
        summary {
            color: red !important;
        }

        summary:hover, summary:focus {
            color: white !important;
        }  
         
    </style>
""", unsafe_allow_html=True)

    # Create the styled login box
    with st.container():
        st.markdown("""
        <div class="login-box">
            <div style="text-align: center;">
                <img src="https://images.seeklogo.com/logo-png/31/1/indian-railways-logo-png_seeklogo-310214.png" width="200">
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-title" style="color: white; text-align: center;">INDIAN RAILWAY LOGIN</div>', unsafe_allow_html=True)


        # Streamlit widgets inside styled container
        username = st.text_input("", placeholder="User ID", key="login_user", label_visibility="collapsed")
        password = st.text_input("", placeholder="Password", type="password", key="login_pass", label_visibility="collapsed")

        st.markdown("""
            <style>
            /* Try all possible label paths for checkbox */
            label, .stCheckbox label, .stCheckbox div, div[data-testid="stCheckbox"] > div {
                color: white !important;
                font-size: 16px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        remember = st.checkbox("Remember Me")

        login_clicked = st.button("Login", key="login_btn", use_container_width=True)

        # Login logic
        if login_clicked:
            role = login_user(username, password)  # Replace with your actual login logic
            if role:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.session_state.remember_me = remember
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

        st.markdown('<div class="footer">© 2025 Indian Railways | IT Division</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def send_otp_email(email, username):
        otp = str(random.randint(100000, 999999))
        st.session_state.generated_otp = otp
        st.session_state.otp_user = username


        msg = EmailMessage()
        msg.set_content(f"Your OTP to reset your password is: {otp}")
        msg["Subject"] = "Indian Railways Password Reset OTP"
        msg["From"] = "msign9187@gmail.com"
        msg["To"] = email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login("msign9187@gmail.com", "sftxqwselknbmrse")  # Make sure this is correct
                smtp.send_message(msg)
            return True
        except Exception as e:
            st.error(f"❌ Email send error: {e}")
            return False

            return False
        
    with st.expander("Forgot Password?"):
        username_forgot = st.text_input("Enter your username", key="forgot_username")

        if st.button("Send OTP", key="send_otp_btn"):
            conn = create_connection()
            cur = conn.cursor()
            try:
                # Ensure username is compared case-insensitively and stripped
                cur.execute("""
                    SELECT email FROM users 
                    WHERE LOWER(TRIM(username)) = LOWER(:username)
                """, {"username": username_forgot.strip()})
                result = cur.fetchone()
            finally:
                cur.close()
                conn.close()

            if result:
                email = result[0]
                success = send_otp_email(email, username_forgot)
                if success:
                    st.success(f"OTP sent to {email}")
                    st.session_state.otp_user = username_forgot
                    st.session_state.otp_sent = True
                else:
                    st.error("❌ Failed to send OTP.")
            else:
                st.error("❌ Username not found. Please check spelling or case.")


    if st.session_state.get("otp_sent"):
        entered_otp = st.text_input("Enter OTP sent to your email")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            if entered_otp.strip() == st.session_state.get("generated_otp", ""):

                # Update password
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("UPDATE users SET password_hash=:1 WHERE username=:2",
                            (hash_password(new_pass), st.session_state.otp_user))
                conn.commit()
                cur.close()
                conn.close()
                st.success("✅ Password updated. You can now login.")
                del st.session_state["otp_sent"]
                del st.session_state["otp_user"]
            else:
                st.error("Invalid OTP.")

    def users_page():
        st.title("👥 User Management")

        current_user = st.session_state.get("username", "system")  # Logged-in user

        # --- CREATE USER ---
        with st.expander("➕ Create New User"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "employee"])
            email = st.text_input("Email", placeholder="Enter user's email")

            if st.button("Create User"):
                if not new_username.strip() or not new_password.strip() or not email.strip():
                    st.warning("Please fill in all fields: Username, Password, and Email.")
                else:
                    result = signup_user(new_username, new_password, new_role, email, current_user)
                    if result is True:
                        st.success("User created successfully!")
                    else:
                        st.error(result)

        # --- ASSIGN PAGE ACCESS ---
        with st.expander("🛡 Assign Page Access"):
            employees = get_all_employees()
            if not employees:
                st.info("No employees found.")
            else:
                selected_employee = st.selectbox("Select Employee", employees)
                current_access = get_employee_permissions(selected_employee)
                selected_pages = st.multiselect(
                    "Assign Pages",
                    ["Dashboard", "Revenue Analytics", "Data Exporter", "Data Entry & CRUD"],
                    default=current_access
                )
                if st.button("Update Access"):
                    set_employee_access(selected_employee, selected_pages)
                    st.success("Access updated.")

        # --- VIEW & MANAGE USERS ---
        with st.expander("📋 View & Manage Users"):
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, email, is_active, created_by, modified_by, created_at, last_updated FROM users ORDER BY id")
            users = cursor.fetchall()
            cursor.close()
            conn.close()

            df = pd.DataFrame(users, columns=["ID", "Username", "Role", "Email", "Active", "Created By", "Modified By", "Created At", "Last Updated"])
            st.dataframe(df, use_container_width=True)

            selected_id = st.selectbox("Select User ID", df["ID"])
            action = st.radio("Action", ["Update Info", "Disable User", "Enable User", "Delete Permanently"])

            if action == "Update Info":
                conn = create_connection()
                cur = conn.cursor()
                cur.execute("SELECT username, email FROM users WHERE id = :1", (selected_id,))
                current_username, current_email = cur.fetchone()
                cur.close()
                conn.close()

                updated_username = st.text_input("New Username", value=current_username)
                updated_email = st.text_input("New Email", value=current_email)
                updated_password = st.text_input("New Password (leave blank to keep current)", type="password")
                updated_role = st.selectbox("New Role", ["admin", "employee"])

                if st.button("Update User"):
                    conn = create_connection()
                    cur = conn.cursor()

                    try:
                        cur.execute("SELECT username, email FROM users WHERE id = :1", (selected_id,))
                        current_username, current_email = cur.fetchone()

                        if updated_password.strip() == "":
                            cur.execute("""
                                UPDATE users 
                                SET username = :1, role = :2, email = :3, last_updated = SYSTIMESTAMP, modified_by = :4
                                WHERE id = :5
                            """, (updated_username, updated_role, updated_email, current_user, selected_id))
                        else:
                            cur.execute("""
                                UPDATE users 
                                SET username = :1, password_hash = :2, role = :3, email = :4, last_updated = SYSTIMESTAMP, modified_by = :5
                                WHERE id = :6
                            """, (updated_username, hash_password(updated_password), updated_role, updated_email, current_user, selected_id))

                        cur.execute("UPDATE user_permissions SET username = :1 WHERE username = :2",
                                    (updated_username, current_username))

                        conn.commit()
                        st.success("User updated successfully.")

                    except oracledb.IntegrityError as e:
                        if "ORA-02292" in str(e):
                            st.error("❌ Cannot update username. Please remove all assigned pages first.")
                        else:
                            st.error(f"Failed to update user: {str(e)}")
                    finally:
                        cur.close()
                        conn.close()
            
            elif action == "Enable User":
                if st.button("Enable"):
                    conn = create_connection()
                    cur = conn.cursor()
                    try:
                        cur.execute(
                            "UPDATE users SET is_active='Y', modified_by = :1, last_updated = SYSTIMESTAMP WHERE id = :2",
                            (st.session_state.username, selected_id)
                        )
                        conn.commit()
                        st.success(f"✅ User enabled by {st.session_state.username}.")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error enabling user: {e}")
                    finally:
                        cur.close()
                        conn.close()

            elif action == "Disable User":
                if st.button("Disable"):
                    conn = create_connection()
                    cur = conn.cursor()
                    try:
                        cur.execute(
                            "UPDATE users SET is_active='N', modified_by = :1, last_updated = SYSTIMESTAMP WHERE id = :2",
                            (st.session_state.username, selected_id)
                        )
                        conn.commit()
                        st.success(f"✅ User disabled by {st.session_state.username}.")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error disabling user: {e}")
                    finally:
                        cur.close()
                        conn.close()


            elif action == "Delete Permanently":
                if st.button("Delete User Permanently"):
                    try:
                        conn = create_connection()
                        cur = conn.cursor()
                        cur.execute("SELECT username FROM users WHERE id = :1", (selected_id,))
                        result = cur.fetchone()
                        if result:
                            username = result[0]
                            cur.execute("DELETE FROM user_permissions WHERE username = :1", (username,))
                            cur.execute("DELETE FROM users WHERE id = :1", (selected_id,))
                            conn.commit()
                            st.success("🗑 User permanently deleted.")
                        else:
                            st.warning("User not found.")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error deleting user: {str(e)}")
                    finally:
                        cur.close()
                        conn.close()


