import os
from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DB_PATH = 'weather.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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
        data = request.get_json(force=True, silent=True)
        if not data: return jsonify({"status": "error"}), 400
        
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        timestamp_str = ist_time.strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO readings (timestamp, temp, pres) VALUES (?, ?, ?)",
                      (timestamp_str, data.get('temp'), data.get('pres')))
            conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data')
def get_data():
    ist_today = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Fetch data for chart and Sentry algorithm
        c.execute("SELECT timestamp, temp, pres FROM readings ORDER BY id DESC LIMIT 150")
        rows = c.fetchall()
        
        # Calculate Daily Extremes
        c.execute("""SELECT MAX(temp), MIN(temp), MAX(pres), MIN(pres) 
                     FROM readings WHERE timestamp LIKE ?""", (f"{ist_today}%",))
        extremes = c.fetchone()

    data = [{ 'timestamp': r[0], 'temp': r[1], 'pres': r[2] } for r in rows][::-1]
    
    return jsonify({
        "history": data,
        "extremes": {
            "max_temp": extremes[0] or 0, "min_temp": extremes[1] or 0,
            "max_pres": extremes[2] or 0, "min_pres": extremes[3] or 0
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)