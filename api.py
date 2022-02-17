import json
from flask import Flask, request, jsonify
from engine import Engine
from firebase_db_interface import FirebaseDBInterface
from threading import Event

app = Flask(__name__)

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



if __name__ == "__main__":
    firebase = FirebaseDBInterface()
    engine = Engine(firebase, Event())
    engine.start()
    app.run(host='0.0.0.0', port=80)