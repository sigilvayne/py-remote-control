import time
import requests
import subprocess
import json

config = json.load(open("C:/Script/agent/config.json"))
server_id = config["server_id"]
url = config["control_center_url"]

while True:
    r = requests.get(f"{url}/get_command/{server_id}")
    cmd = r.json().get("command")
    if cmd:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        requests.post(f"{url}/post_result/{server_id}", json={
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode
        })
    time.sleep(5)
