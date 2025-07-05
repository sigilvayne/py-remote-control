import time
import requests
import subprocess
import json
import os

cfg = json.load(open("C:/Script/agent/config.json"))
sid = cfg["server_id"]
url = cfg["control_center_url"]

SCRIPT_DIR = "C:/Script/agent/tmp"
os.makedirs(SCRIPT_DIR, exist_ok=True)

while True:
    try:
        r = requests.get(f"{url}/agent_get_command/{sid}")
        r.raise_for_status()
        cmd = r.json().get("command")

        if cmd:
            if cmd.startswith("download_and_run_script"):
                parts = cmd.strip().split()
                if len(parts) == 2:
                    script_name = parts[1]
                    script_url = f"{url}/scripts/{script_name}"
                    local_path = os.path.join(SCRIPT_DIR, script_name)

                    # Завантаження скрипта
                    script_res = requests.get(script_url)
                    with open(local_path, "wb") as f:
                        f.write(script_res.content)

                    # Визначаємо розширення (ps1, bat, cmd...)
                    ext = os.path.splitext(script_name)[1].lower()

                    if ext == ".ps1":
                        res = subprocess.run([
                            "powershell",
                            "-ExecutionPolicy", "Bypass",
                            "-File", local_path
                        ], capture_output=True, text=True)
                    elif ext in [".bat", ".cmd"]:
                        res = subprocess.run(local_path, shell=True, capture_output=True, text=True)
                    else:
                        res = subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Невідомий тип скрипта.")
                else:
                    res = subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Неправильний формат команди.")
            else:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            requests.post(f"{url}/agent_post_result/{sid}", json={
                "stdout": res.stdout,
                "stderr": res.stderr,
                "code": res.returncode
            })

    except Exception as e:
        pass

    time.sleep(5)
