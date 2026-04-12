import sqlite3

def get_connection():
    return sqlite3.connect("database.db")


def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        username = username.strip().lower()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)

        cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )

        if cursor.fetchone():
            return False

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )

        conn.commit()
        return True

    except Exception as e:
        print("REGISTER ERROR:", e)
        return False

    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    username = username.strip().lower()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE role='student'")
    students = [{"username": row[0]} for row in cursor.fetchall()]

    conn.close()
    return students