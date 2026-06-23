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
