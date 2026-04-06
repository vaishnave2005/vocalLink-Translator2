import sqlite3
import hashlib

DB_PATH = 'sofia.db'

def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (email TEXT, original TEXT, translated TEXT, mode TEXT,
                  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (email, _hash(password)))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, _hash(password)))
    user = c.fetchone()
    conn.close()
    return user

def save_history(email, original, translated, mode):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (email, original, translated, mode) VALUES (?, ?, ?, ?)",
              (email, original, translated, mode))
    conn.commit()
    conn.close()

def get_history(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT original, translated, mode, time FROM history WHERE email=? ORDER BY time DESC",
              (email,))
    data = c.fetchall()
    conn.close()
    return data