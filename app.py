from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    # Table structure: ID, ISO Timestamp, Temperature, Pressure
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, temp REAL, pres REAL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.get_json()
        temp = data.get('temp')
        pres = data.get('pres')
        
        # Use ISO format for easier JavaScript parsing
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('weather.db')
        c = conn.cursor()
        c.execute("INSERT INTO readings (timestamp, temp, pres) VALUES (?, ?, ?)",
                  (now, temp, pres))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_data')
def get_data():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    # Get last 100 readings, newest first
    c.execute("SELECT id, timestamp, temp, pres FROM readings ORDER BY id DESC LIMIT 100")
    data = c.fetchall()
    conn.close()
    # This returns: [[id, time, temp, pres], [id, time, temp, pres]...]
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)