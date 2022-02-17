#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from engine import Engine
from firebase_db_interface import FirebaseDBInterface
from threading import Event

app = Flask(__name__)
firebase = FirebaseDBInterface()
engine = Engine(firebase, Event())
engine.start()

@app.route('/newbot', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    message = "Engine received match set request successfully. Simulating now!"
    try:
        engine.handle_request(record)
    except Exception as e:
        print(e)
        message = str(e)

    return jsonify({"status": message})

app.run(debug=True)