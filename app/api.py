from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
commands = {}
results = {}

@app.route('/set_command/<server_id>', methods=['POST'])
def set_command(server_id):
    commands[server_id] = request.json
    return jsonify({"status": "command_set"})

@app.route('/get_command/<server_id>', methods=['GET'])
def get_command(server_id):
    cmd = commands.pop(server_id, None)
    return jsonify(cmd if cmd else {"status": "no_command"})

@app.route('/post_result/<server_id>', methods=['POST'])
def post_result(server_id):
    results[server_id] = request.json
    return jsonify({"status": "result_received"})

@app.route('/get_result/<server_id>', methods=['GET'])
def get_result(server_id):
    res = results.pop(server_id, None)
    return jsonify(res if res else {"status": "no_result"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
