from flask import Flask, request, jsonify

app = Flask(__name__)
commands = {}

@app.route('/set_command/<server_id>', methods=['POST'])
def set_command(server_id):
    commands[server_id] = request.json
    return jsonify({"status": "command_set"})

@app.route('/get_command/<server_id>', methods=['GET'])
def get_command(server_id):
    cmd = commands.pop(server_id, None)
    return jsonify(cmd if cmd else {"status": "no_command"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})
