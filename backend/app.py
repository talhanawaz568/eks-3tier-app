import os, socket
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"], dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
        connect_timeout=3)

@app.route("/api/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/api/visit")
def visit():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS visits "
                    "(id SERIAL PRIMARY KEY, pod TEXT, ts TIMESTAMP DEFAULT now())")
        cur.execute("INSERT INTO visits (pod) VALUES (%s)", (socket.gethostname(),))
        cur.execute("SELECT count(*) FROM visits")
        total = cur.fetchone()[0]
    return jsonify(total_visits=total, served_by=socket.gethostname())

@app.route("/api/load")
def load():
    # deliberately CPU-heavy, used only to trigger the HPA
    x = 0
    for i in range(3_000_000):
        x += i * i
    return jsonify(done=True, served_by=socket.gethostname())
