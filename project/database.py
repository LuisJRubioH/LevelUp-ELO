import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="elo_project.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de intentos/progreso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                is_correct BOOLEAN,
                difficulty INTEGER,
                topic TEXT,
                elo_after REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user if user else None

    def save_attempt(self, user_id, item_id, is_correct, difficulty, topic, elo_after):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attempts (user_id, item_id, is_correct, difficulty, topic, elo_after)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, item_id, is_correct, difficulty, topic, elo_after))
        conn.commit()
        conn.close()

    def get_user_history_elo(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows] if rows else [1000] # Valor inicial por defecto

    def get_latest_elo(self, user_id):
        history = self.get_user_history_elo(user_id)
        return history[-1]

    def get_attempts_for_ai(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT topic, difficulty, is_correct, timestamp 
            FROM attempts 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        conn.close()
        return results

    def get_answered_item_ids(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_id FROM attempts WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_latest_elo_by_topic(self, user_id):
        """Devuelve un diccionario {topic: elo_actual} para el usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Traemos todo ordenado por fecha y actualizamos el dict.
        # El último valor sobreescribirá a los anteriores para ese topic.
        cursor.execute("SELECT topic, elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        elo_map = {}
        for topic, elo in rows:
            elo_map[topic] = elo
        return elo_map

    def get_user_history_full(self, user_id):
        """Devuelve historial completo para gráficas: [{'timestamp':..., 'topic':..., 'elo':...}]"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, topic, elo_after FROM attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'topic': r[1], 'elo': r[2]} for r in rows]
