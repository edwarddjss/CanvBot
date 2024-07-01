import sqlite3
import asyncio

def init_db():
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys
               (user_id INTEGER PRIMARY KEY, api_key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_courses (
    user_id INTEGER,
    course_id INTEGER,
    course_name TEXT,
    PRIMARY KEY (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES api_keys(user_id))''')
    conn.commit()
    conn.close()

    
async def get_api_key(user_id):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_api_key_sync, user_id)

def _get_api_key_sync(user_id):
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM api_keys WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_id():
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM api_keys")
    results = cursor.fetchall()
    conn.close()
    return [result[0] for result in results]

def insert_api_key(user_id, api_key):
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api_keys (user_id, api_key) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET api_key = excluded.api_key", (user_id, api_key))
    conn.commit()
    conn.close()
    
def insert_user_course(user_id, course_id, course_name):
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_courses (user_id, course_id, course_name) VALUES (?, ?, ?) ON CONFLICT(user_id, course_id) DO UPDATE SET course_name = excluded.course_name", (user_id, course_id, course_name))
    conn.commit()
    conn.close()

def get_course_id_by_name(user_id, course_name):
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("SELECT course_id FROM user_courses WHERE user_id = ? AND course_name = ?", (user_id, course_name))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

    
def get_course_ids(user_id):
    conn = sqlite3.connect('api_keyss.db')
    cursor = conn.cursor()
    cursor.execute("SELECT course_id FROM user_courses WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    conn.close()
    return [result[0] for result in results]


