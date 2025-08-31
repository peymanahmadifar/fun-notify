from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, time, os

DB_PATH = "data/notify.db"

app = Flask(__name__, static_folder="static")
CORS(app)

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY,
        last_seen REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS pings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        created REAL
    )""")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.json["name"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (name, time.time()))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/users")
def users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM users")
    names = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(names)

@app.route("/ping", methods=["POST"])
def ping():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO pings (sender,receiver,created) VALUES (?,?,?)",
              (data["sender"], data["receiver"], time.time()))
    conn.commit()
    conn.close()
    return jsonify({"status":"ping sent"})

@app.route("/check/<user>")
def check(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sender FROM pings WHERE receiver=? ORDER BY created DESC", (user,))
    rows = c.fetchall()
    c.execute("DELETE FROM pings WHERE receiver=?", (user,))
    conn.commit()
    conn.close()
    return jsonify([r[0] for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
