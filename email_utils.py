import smtplib
import random
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    email_sender = os.getenv("SENDER_EMAIL")
    email_password = os.getenv("SENDER_PASS")  # Use app password (not your Gmail password)

    if not email_sender or not email_password:
        try:
            import streamlit as st
            email_sender = email_sender or st.secrets.get("SENDER_EMAIL")
            email_password = email_password or st.secrets.get("SENDER_PASS")
        except Exception:
            pass

    subject = 'Password Reset OTP for SupportiveGPT'
    body = f'Your OTP for password reset is: {otp}'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_sender
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False




# User clicks "Forgot Password"
#             │
#             ▼
# generate_otp()
#             │
#             ▼
# Random 6-digit OTP generated
#             │
#             ▼
# send_otp_email(email, otp)
#             │
#             ▼
# Read Sender Email & App Password from .env
#             │
#             ▼
# Create EmailMessage (To, From, Subject, Body)
#             │
#             ▼
# Connect to Gmail SMTP Server (smtp.gmail.com:587)
#             │
#             ▼
# Enable TLS Encryption (starttls)
#             │
#             ▼
# Login using Gmail App Password
#             │
#             ▼
# Send OTP Email
#             │
#      ┌──────┴──────┐
#      ▼             ▼
# Success         Failure
# (return True) (return False)


### Interview Questions You Should Be Ready For ###
# Why do we use smtplib?
# To send emails from a Python application using the SMTP protocol.
# Why use load_dotenv()?
# To load sensitive information like email credentials from a .env file instead of hardcoding them.
# Why is os.getenv() used?
# To securely read environment variables loaded from the .env file.
# Why use a Gmail App Password instead of the Gmail account password?
# Google blocks normal passwords for many third-party apps. An App Password is a more secure way to allow SMTP access without exposing the main account password.
# Why is starttls() important?
# It encrypts the connection between your application and Gmail's server so credentials and email data are transmitted securely.
# Why is the OTP converted to a string?
# Because it is inserted into the email text, and email content is handled as strings.
# Why use a try-except block?
# To prevent the application from crashing if email sending fails and to handle errors gracefully.




# Here's a concise, interview-ready summary you can memorize in 30–40 seconds:

# email_utils.py is responsible for the OTP-based password recovery feature. 
# It first generates a random 6-digit OTP using Python's random module. 
# Then it reads the sender's email credentials securely from the .env file using dotenv and os.getenv(). 
# It creates an email with the OTP using the EmailMessage class and 
# sends it through Gmail's SMTP server (smtp.gmail.com) over a secure TLS connection.
# Exception handling (try-except) is used to handle errors gracefully, 
# and the function returns True if the email is sent successfully, otherwise False.

# One-line version (15 seconds)
# email_utils.py generates a secure 6-digit OTP and sends it to the user's email using Gmail SMTP with TLS encryption, 
# while keeping email credentials secure through environment variables and handling failures with exception handling. 

