from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading
import os
from flask import send_from_directory
import uuid
from io import BytesIO
import zipfile
from flask import send_file



app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'servers.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.secret_key = 'very_secret_key_123'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Session(app)
db = SQLAlchemy(app)

#---------------------Database init-------------------#

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.String(100), unique=True, nullable=False)
    control_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Server {self.server_id}>"

with app.app_context():
    db.create_all()

#---------------------Autentication-------------------#

users = {'marusiak': 'admin123'}

commands = {}  # server_id -> {"id": ..., "command": ...}
results = {}   # server_id -> {"id": ..., "stdout": ..., ...}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

#---------------------Web endpoints--------------------#

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

@app.route('/servers', methods=['GET'])
@login_required
def list_servers():
    servers = Server.query.order_by(Server.created_at.desc()).all()
    return jsonify([s.server_id for s in servers])



#---------------------Commands control--------------------#

@app.route('/set_command/<server_id>', methods=['POST'])
@login_required
def set_command(server_id):
    payload = request.json or {}
    command = payload.get("command", "")
    command_id = str(uuid.uuid4())

    commands[server_id] = {
        "id": command_id,
        "command": command
    }
    return jsonify({"status": "command_set", "command_id": command_id})

@app.route('/get_result/<server_id>', methods=['GET'])
@login_required
def get_result(server_id):
    expected_id = request.args.get("command_id")
    res = results.get(server_id)
    if res and res.get("id") == expected_id:
        results.pop(server_id)
        return jsonify(res)
    else:
        return jsonify({"status": "no_result"})

@app.route('/get_medoc_version', methods=['GET'])
def get_medoc_version():
    try:
        with open('scripts/variables/medoc-ver.txt', 'r', encoding='utf-8') as f:
            version = f.read().strip()
        return jsonify({"version": version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#---------------------Scripts loader--------------------#

@app.route('/scripts/<path:filename>')
def serve_script(filename):
    return send_from_directory('scripts', filename)


# --- Агент API ---
@app.route('/agent_get_command/<server_id>', methods=['GET'])
def agent_get_command(server_id):
    cmd = commands.pop(server_id, None)
    return jsonify(cmd if cmd else {"status": "no_command"})

@app.route('/agent_post_result/<server_id>', methods=['POST'])
def agent_post_result(server_id):
    result = request.json or {}
    # result має містити "id", "stdout", "stderr" тощо
    results[server_id] = result
    return jsonify({"status": "result_received"})

# --- Реєстрація серверів  ---
@app.route('/register_server', methods=['POST'])
def register_server():
    data = request.get_json()
    server_id = data.get("server_id")
    control_url = data.get("control_center_url")

    if not server_id or not control_url:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    existing = Server.query.filter_by(server_id=server_id).first()
    if existing:
        return jsonify({"status": "exists", "message": "Server already registered"}), 200

    new_server = Server(server_id=server_id, control_url=control_url)
    db.session.add(new_server)
    db.session.commit()
    return jsonify({"status": "ok", "message": "Server registered"}), 201

#--------------------Bases--------------------#

@app.route('/base')
@login_required
def base():
    servers = Server.query.order_by(Server.created_at.desc()).all()
    return render_template('base.html', servers=servers, username=session['username'])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

#---------------------Deleting server from list--------------------#

@app.route('/delete_server/<int:server_id>', methods=['POST'])
@login_required
def delete_server(server_id):
    server = Server.query.get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    return redirect(url_for('base'))


#---------------------Download installer--------------------#

@app.route('/download', methods=['GET'])
@login_required
def download_installer():
    installer_dir = os.path.join(basedir, 'installer')

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(installer_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, installer_dir)
                zf.write(file_path, arcname)
    memory_file.seek(0)

    return send_file(
        memory_file,
        download_name='installer.zip',
        as_attachment=True,
        mimetype='application/zip'
    )
