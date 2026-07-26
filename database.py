import sqlite3

def init_db():
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, role TEXT, warns INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

def get_user_role(user_id):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def set_user_role(user_id, role):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, role) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET role = excluded.role", (user_id, role))
    conn.commit()
    conn.close()

def add_user_warn(user_id):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, warns) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET warns = warns + 1", (user_id,))
    cursor.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,))
    warns = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return warns

def reset_user_warns(user_id):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET warns = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_log_chat():
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'log_peer_id'")
    res = cursor.fetchone()
    conn.close()
    return int(res[0]) if res else None

def set_log_chat(peer_id):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO settings (key, value) VALUES ('log_peer_id', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (str(peer_id),))
    conn.commit()
    conn.close()

def set_chat_name(peer_id, chat_name):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    key = f"chat_name_{peer_id}"
    cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, chat_name))
    conn.commit()
    conn.close()

def get_chat_name(peer_id):
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    key = f"chat_name_{peer_id}"
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else f"❓ Неизвестный чат ({peer_id})"

