from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os
import uuid
import bcrypt
import json

#---------------------Init-------------------#

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'servers.db')
users_path = os.path.join(basedir, 'user.json')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'secret')
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
db = SQLAlchemy(app)

#---------------------DB Models-------------------#

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.String(100), unique=True, nullable=False)
    control_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Server {self.server_id}>"

with app.app_context():
    db.create_all()

#---------------------User Management (JSON)-------------------#

def load_users():
    if not os.path.exists(users_path):
        return {}
    with open(users_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(users_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

def validate_login(username, password):
    users = load_users()
    user = users.get(username)
    if not user or not user.get('active', True):
        return False
    stored_hash = user.get('password')
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

#---------------------Auth-------------------#

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if validate_login(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Невірний логін або пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#---------------------User Control-------------------#

@app.route('/user_control', methods=['GET'])
@login_required
def user_control():
    users = load_users()
    return render_template('user-control.html', users=users, username=session['username'])

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    data = request.form
    users = load_users()
    username = data['username']
    if username in users:
        return redirect(url_for('user_control'))
    
    raw_password = data['password'].strip()
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users[username] = {
        "password": hashed,
        "role": data.get('role', 'viewer'),
        "active": data.get('active') == 'on'
    }
    save_users(users)
    return redirect(url_for('user_control'))

@app.route('/delete_user/<username>', methods=['POST'])
@login_required
def delete_user(username):
    users = load_users()
    if username in users:
        users.pop(username)
        save_users(users)
    return redirect(url_for('user_control'))

#---------------------Agent Security-------------------#

AGENT_TOKEN = os.getenv("AGENT_TOKEN")

def agent_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token") or request.headers.get("X-Agent-Token")
        if token != AGENT_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

#---------------------Web Pages-------------------#

@app.route('/')
@login_required
def index():
    return render_template("connection.html", username=session['username'])

@app.route('/monitoring')
@login_required
def monitoring():
    return render_template("monitoring.html", username=session['username'])

@app.route('/base')
@login_required
def base():
    servers = Server.query.order_by(Server.created_at.desc()).all()
    return render_template('base.html', servers=servers, username=session['username'])

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

#---------------------Server Management-------------------#

@app.route('/servers')
@login_required
def list_servers():
    servers = Server.query.order_by(Server.created_at.desc()).all()
    return jsonify([s.server_id for s in servers])

@app.route('/register_server', methods=['POST'])
@agent_auth_required
def register_server():
    data = request.get_json()
    server_id = data.get("server_id")
    control_url = data.get("control_center_url")

    if not server_id or not control_url:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    existing = Server.query.filter_by(server_id=server_id).first()
    if existing:
        return jsonify({"status": "exists", "message": "Server already registered"})

    new_server = Server(server_id=server_id, control_url=control_url)
    db.session.add(new_server)
    db.session.commit()
    return jsonify({"status": "ok", "message": "Server registered"}), 201

@app.route('/delete_server/<int:server_id>', methods=['POST'])
@login_required
def delete_server(server_id):
    server = Server.query.get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    return redirect(url_for('base'))

#---------------------Commands-------------------#

commands = {}
results = {}

@app.route('/set_command/<server_id>', methods=['POST'])
@login_required
def set_command(server_id):
    payload = request.json or {}
    command = payload.get("command", "")
    command_id = str(uuid.uuid4())
    commands[server_id] = {"id": command_id, "command": command}
    return jsonify({"status": "command_set", "command_id": command_id})

@app.route('/get_result/<server_id>', methods=['GET'])
@login_required
def get_result(server_id):
    expected_id = request.args.get("command_id")
    res = results.get(server_id)
    if res and res.get("id") == expected_id:
        results.pop(server_id)
        return jsonify(res)
    return jsonify({"status": "no_result"})

#---------------------Agent Interface-------------------#

@app.route('/agent_get_command/<server_id>', methods=['GET'])
@agent_auth_required
def agent_get_command(server_id):
    cmd = commands.pop(server_id, None)
    return jsonify(cmd if cmd else {"status": "no_command"})

@app.route('/agent_post_result/<server_id>', methods=['POST'])
@agent_auth_required
def agent_post_result(server_id):
    results[server_id] = request.json or {}
    return jsonify({"status": "result_received"})

#---------------------Misc-------------------#

@app.route('/scripts/<path:filename>')
def serve_script(filename):
    return send_from_directory('scripts', filename)

@app.route('/get_medoc_version')
def get_medoc_version():
    try:
        with open('scripts/variables/medoc-ver.txt', 'r', encoding='utf-8') as f:
            version = f.read().strip()
        return jsonify({"version": version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#---------------------Start-------------------#

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
