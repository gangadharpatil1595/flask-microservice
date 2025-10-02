from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://flaskuser:flaskpass@microservice-db:5432/flaskdb")
SKIP_DB = os.getenv("SKIP_DB", "false").lower() == "true"

def get_db_connection():
    if SKIP_DB:
        print("[INFO] Running in no-DB mode, skipping database connection.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"[WARN] Could not connect to database: {e}")
        return None

def init_db():
    if SKIP_DB:
        print("[INFO] Skipping DB initialization in no-DB mode.")
        return
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Example table init
        cur.execute("CREATE TABLE IF NOT EXISTS messages (id serial PRIMARY KEY, content text);")
        conn.commit()
        cur.close()
        conn.close()

@app.route('/')
def index():
    if SKIP_DB:
        return "✅ Flask app is running in no-DB mode!", 200
    conn = get_db_connection()
    if not conn:
        return "⚠️ DB unavailable", 500
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return f"Messages: {rows}"

@app.route('/add', methods=['POST'])
def add_message():
    if SKIP_DB:
        return "❌ DB disabled in this deployment", 200
    content = request.form['content']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (content) VALUES (%s)", (content,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not SKIP_DB:
        init_db()
    app.run(host='0.0.0.0', port=5000)
