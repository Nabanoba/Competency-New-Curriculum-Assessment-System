import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ai_competency_system"
    )

# =========================
# REGISTER USER (FIXED)
# =========================
def register_user(username, password, role):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        username = username.strip().lower()

        # check duplicate
        cursor.execute(
            "SELECT id FROM users WHERE LOWER(username)=%s",
            (username,)
        )

        if cursor.fetchone():
            return False  # already exists

        cursor.execute(
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
    cursor = conn.cursor()

    try:
        username = username.strip().lower()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        return cursor.fetchone()

    finally:
        conn.close()


# =========================
# GET ALL STUDENTS (NEW ⭐)
# =========================
def get_all_students():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT username FROM users WHERE role='student'")

    students = cursor.fetchall()

    conn.close()
    return students