import time
import requests
import subprocess
import json
config = json.load(open("C:/Script/agent/config.json"))
server_id = config["server_id"]
url = config["control_center_url"]

while True:
    try:
        r = requests.get(f"{url}/agent_get_command/{server_id}")
        r.raise_for_status()

        data = r.json()
        cmd = data.get("command")

        if cmd:
            print(f"[INFO] Виконання команди: {cmd}")
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            response = {
                "stdout": res.stdout,
                "stderr": res.stderr,
                "code": res.returncode
            }
            print(f"[INFO] Відправка результату: {response}")
            requests.post(f"{url}/agent_post_result/{server_id}", json=response)
        else:
            print("[INFO] Команд нема")

    except Exception as e:
        print(f"[ERROR] Виникла помилка: {e}")

    time.sleep(5)
