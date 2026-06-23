import mysql.connector
from dotenv import load_dotenv
import os
import base64

load_dotenv()

def get_connection():
    ssl_ca_path = None
    b64_cert = os.environ.get("CA_CERT_B64")
    db_ca = os.getenv("DB_CA")

    # Decode the CA certificate from environment variable if provided
    if b64_cert and b64_cert.strip():
        os.makedirs("certs", exist_ok=True)
        cert_path = "certs/ca.pem"
        try:
            with open(cert_path, "wb") as cert_file:
                cert_file.write(base64.b64decode(b64_cert.strip()))
            ssl_ca_path = cert_path
        except Exception as e:
            print("Failed to decode CA_CERT_B64:", e)
    # Or check if local DB_CA file exists
    elif db_ca and os.path.exists(db_ca):
        ssl_ca_path = db_ca

    connect_args = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB"),
        "port": os.getenv("DB_PORT")
    }

    if ssl_ca_path:
        connect_args["ssl_ca"] = ssl_ca_path

    return mysql.connector.connect(**connect_args)

