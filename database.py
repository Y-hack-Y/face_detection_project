import sqlite3
import os
import hashlib

DB_PATH = 'face_detection.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encoding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            detected_name TEXT,
            confidence REAL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('admin', admin_password, 'admin')
        )
    except sqlite3.IntegrityError:
        pass
    
    user_password = hashlib.sha256('user123'.encode()).hexdigest()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('user', user_password, 'user')
        )
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def add_face(name, encoding):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    encoding_blob = encoding.tobytes()
    cursor.execute(
        'INSERT INTO faces (name, encoding) VALUES (?, ?)',
        (name, encoding_blob)
    )
    
    conn.commit()
    face_id = cursor.lastrowid
    conn.close()
    
    return face_id

def get_all_faces():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM faces')
    faces = cursor.fetchall()
    conn.close()
    
    return [dict(face) for face in faces]

def delete_face(face_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM faces WHERE id = ?', (face_id,))
    conn.commit()
    conn.close()

def add_detection_log(user_id, detected_name, confidence, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO detection_logs (user_id, detected_name, confidence, image_path) VALUES (?, ?, ?, ?)',
        (user_id, detected_name, confidence, image_path)
    )
    
    conn.commit()
    conn.close()

def get_detection_logs(user_id=None, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute(
            'SELECT * FROM detection_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
    else:
        cursor.execute(
            'SELECT * FROM detection_logs ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )
    
    logs = cursor.fetchall()
    conn.close()
    
    return [dict(log) for log in logs]

def add_to_blacklist(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO blacklist (name) VALUES (?)',
            (name,)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    finally:
        conn.close()
    
    return result

def remove_from_blacklist(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM blacklist WHERE name = ?', (name,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0

def is_blacklisted(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM blacklist WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def get_all_blacklist():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM blacklist')
    blacklist = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in blacklist]

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成！")
    print("默认账号：")
    print("管理员 - 用户名: admin, 密码: admin123")
    print("普通用户 - 用户名: user, 密码: user123")
