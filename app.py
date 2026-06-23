import streamlit as st
from user_auth import authenticate_user, register_user, check_email_exists, update_user_password
from email_utils import generate_otp, send_otp_email
from sample_app import run_genai_chat

st.set_page_config(page_title="SupportiveGPT", layout="centered")

# Initial session states
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'register_mode' not in st.session_state:
    st.session_state.register_mode = False
if 'forgot_password_mode' not in st.session_state:
    st.session_state.forgot_password_mode = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'verified_email' not in st.session_state:
    st.session_state.verified_email = None
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

# ---------- Forgot Password Flow ----------
if not st.session_state.authenticated:
    if st.session_state.forgot_password_mode:
        st.title("Forgot Password")

        if not st.session_state.otp_sent:
            with st.form("otp_request_form"):
                email = st.text_input("Enter your registered email:")
                submit_otp = st.form_submit_button("Send OTP")
                if submit_otp:
                    if check_email_exists(email):
                        otp = generate_otp()
                        if send_otp_email(email, otp):
                            st.session_state.otp_sent = True
                            st.session_state.verified_email = email
                            st.session_state.generated_otp = otp
                            st.success("OTP sent to your email.")
                        else:
                            st.error("Failed to send OTP. Try again.")
                    else:
                        st.error("Email not found.")
            st.button("Back to Login", on_click=lambda: st.session_state.update({'forgot_password_mode': False}))

        else:
            with st.form("otp_verification_form"):
                otp_input = st.text_input("Enter the OTP sent to your email")
                new_password = st.text_input("Enter New Password", type="password")
                submit_reset = st.form_submit_button("Verify & Reset Password")
                if submit_reset:
                    if otp_input == st.session_state.generated_otp:
                        if update_user_password(st.session_state.verified_email, new_password):
                            st.success("Password reset successful! Please login.")
                            st.session_state.update({
                                'forgot_password_mode': False,
                                'otp_sent': False,
                                'verified_email': None,
                                'generated_otp': None
                            })
                        else:
                            st.error("Error updating password.")
                    else:
                        st.error("Invalid OTP.")

            if st.button("Resend OTP"):
                otp = generate_otp()
                if send_otp_email(st.session_state.verified_email, otp):
                    st.session_state.generated_otp = otp
                    st.success("OTP resent to your email.")
                else:
                    st.error("Failed to resend OTP.")

            st.button("Back to Login", on_click=lambda: st.session_state.update({
                'forgot_password_mode': False,
                'otp_sent': False,
                'verified_email': None,
                'generated_otp': None
            }))

# ---------- Registration Flow ----------
    elif st.session_state.register_mode:
        st.title("Register New User")
        with st.form("register_form"):
            name = st.text_input("Name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            register_submit = st.form_submit_button("Register")

            if register_submit:
                success, error_msg = register_user(name, reg_email, reg_password, gender)
                if success:
                    st.success("Registration successful! Please login.")
                    st.session_state.register_mode = False
                else:
                    if error_msg and ("1062" in error_msg or "Duplicate entry" in error_msg):
                        st.error("Email already exists. Try another one.")
                    else:
                        st.error(f"Registration failed: {error_msg}")

        st.button("Back to Login", on_click=lambda: st.session_state.update({'register_mode': False}))

# ---------- Login Flow ----------
    else:
        st.title("Login to SupportiveGPT")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Login")

            if login_submit:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.name = user['name']
                    st.session_state.gender = user['gender']
                    st.success(f"Welcome, {user['name']}!")
                else:
                    st.error("Invalid credentials")

        st.button("New User? Register", on_click=lambda: st.session_state.update({'register_mode': True}))
        st.button("Forgot Password?", on_click=lambda: st.session_state.update({'forgot_password_mode': True}))

# ---------- Logged In Chat Interface ----------
else:
    st.sidebar.success(f"Logged in as {st.session_state.name}")
    run_genai_chat(st.session_state.name, st.session_state.gender)
