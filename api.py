#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def get_domains():
    domains = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Domains")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            domain = {}
            domain["DomainName"] = i["DomainName"]
            domain["ExpiryDate"] = i["ExpiryDate"]
            domain["DomainStatus"] = i["DomainStatus"]
            domains.append(domain)

    except:
        domains = []

    return domains

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/domains', methods=['GET'])
def api_get_domains():
    return jsonify(get_domains())

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run()