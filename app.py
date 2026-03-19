import os
from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

# This ensures the database is ready as soon as the app starts
def init_db():
    with sqlite3.connect('weather.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS readings 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      timestamp TEXT, temp REAL, pres REAL)''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    try:
        # force=True handles cases where the NodeMCU doesn't send the header perfectly
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400
            
        temp = data.get('temp')
        pres = data.get('pres')
        
        with sqlite3.connect('weather.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO readings (timestamp, temp, pres) VALUES (?, ?, ?)",
                      (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), temp, pres))
            conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data')
def get_data():
    with sqlite3.connect('weather.db') as conn:
        c = conn.cursor()
        c.execute("SELECT timestamp, temp, pres FROM readings ORDER BY id DESC LIMIT 50")
        readings = c.fetchall()
    
    return jsonify([{
        'timestamp': r[0],
        'temp': r[1],
        'pres': r[2]
    } for r in readings])

if __name__ == "__main__":
    # This part is for local testing only; Render uses Gunicorn instead
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)