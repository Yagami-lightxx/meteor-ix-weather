import os

from flask import Flask, request, jsonify, render_template

import sqlite3

from datetime import datetime, timedelta



app = Flask(__name__)



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

        data = request.get_json(force=True, silent=True)

        if not data:

            return jsonify({"status": "error", "message": "No JSON received"}), 400

           

        temp = data.get('temp')

        pres = data.get('pres')

       

        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)

        timestamp_str = ist_time.strftime("%Y-%m-%d %H:%M:%S")

       

        with sqlite3.connect('weather.db') as conn:

            c = conn.cursor()

            c.execute("INSERT INTO readings (timestamp, temp, pres) VALUES (?, ?, ?)",

                      (timestamp_str, temp, pres))

            conn.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:

        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/get_data')

def get_data():

    with sqlite3.connect('weather.db') as conn:

        c = conn.cursor()

        # Increased limit to 120 to ensure we have 2 hours of data for the Sentry algorithm

        c.execute("SELECT timestamp, temp, pres FROM readings ORDER BY id DESC LIMIT 120")

        rows = c.fetchall()

   

    data = [{

        'timestamp': r[0],

        'temp': r[1],

        'pres': r[2]

    } for r in rows][::-1]

   

    return jsonify(data)



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)