import bcrypt
from db_config import get_connection

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_auth WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password(password, user['password']):
            return user
        return None
    except Exception as e:
        print("Login error:", e)
        return None


def register_user(name, email, password, gender):
    try:
        hashed_pw = hash_password(password).decode('utf-8')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_auth (name, email, password, gender) VALUES (%s, %s, %s, %s)",
                       (name, email, hashed_pw, gender))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        print("Registration error:", e)
        return False, str(e)

def check_email_exists(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_auth WHERE email=%s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print("DB Error:", e)
        return False

def update_user_password(email, new_password):
    try:
        hashed_pw = hash_password(new_password).decode('utf-8')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_auth SET password=%s WHERE email=%s", (hashed_pw, email))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("Password update error:", e)
        return False
