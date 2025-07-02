import time, requests, subprocess, json

cfg = json.load(open("C:/Script/agent/config.json"))
sid, url = cfg["server_id"], cfg["control_center_url"]

while True:
    try:
        r = requests.get(f"{url}/agent_get_command/{sid}")
        r.raise_for_status()
        cmd = r.json().get("command")
        if cmd:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            requests.post(f"{url}/agent_post_result/{sid}", json={
                "stdout": res.stdout,
                "stderr": res.stderr,
                "code": res.returncode
            })
    except:
        pass
    time.sleep(5)
