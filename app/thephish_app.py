import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request, escape
from flask_socketio import SocketIO
from ws_logger import WebSocketLogger

import list_emails
import case_from_email
import run_analysis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

from pymongo import MongoClient

# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['thephish']
verdicts_collection = db['verdicts']


@app.route("/")
def homepage():
    return render_template("index.html")

@app.route('/list', methods=['GET'])
def obtain_emails_to_analyze():
    emails_info = list_emails.main()
    return jsonify(emails_info)


from flask import redirect, url_for
@app.route('/analysis', methods=['POST'])
def analyze_email():
    mail_uid = escape(request.form.get("mailUID"))
    sid_client = escape(request.form.get("sid"))
    wsl = WebSocketLogger(socketio, sid_client)
    
    # ✅ Safely handle None return
    result = case_from_email.main(wsl, mail_uid)
    if result is None:
        return "Email could not be analyzed or was already processed.", 400

    new_case_id, external_from_field, subject_text, body_text = result
    
    # ⬇️ Pass them to run_analysis
    verdict = run_analysis.main(wsl, new_case_id, external_from_field, subject_text, body_text, mail_uid)
    return jsonify({"redirect": "/verdicts"})

@app.route('/verdicts')
def show_verdicts():
    verdicts = list(verdicts_collection.find().sort('timestamp', -1))
    return render_template('verdicts.html', verdicts=verdicts)

if __name__ == "__main__":
    print("Starting ThePhish app...")
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)

