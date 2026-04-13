import os
import psycopg2

# =========================
# DATABASE CONNECTION
# =========================
def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# =========================
# INIT DATABASE
# =========================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# REGISTER USER
# =========================
def register_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()

    username = username.strip().lower()
    role = role.strip().lower()

    try:
        # check if user exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return False

        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )

        conn.commit()
        return True

    except Exception as e:
        print("REGISTER ERROR:", e)
        return False

    finally:
        conn.close()


# =========================
# LOGIN USER
# =========================
def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    username = username.strip().lower()

    cur.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()
    return user


# =========================
# GET STUDENTS
# =========================
def get_all_students():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE role = 'student'")
    rows = cur.fetchall()

    conn.close()

    return [{"username": r[0]} for r in rows]