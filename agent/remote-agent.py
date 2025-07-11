import time
import requests
import subprocess
import json
import os

# Завантаження конфігурації
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

                    # Визначаємо розширення
                    ext = os.path.splitext(script_name)[1].lower()

                    if ext == ".ps1":
                        # Виклик PowerShell з примусовим кодуванням UTF-8
                        res = subprocess.run([
                            "powershell",
                            "-ExecutionPolicy", "Bypass",
                            "-Command",
                            f"$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8; & '{local_path}'"
                        ], capture_output=True, text=True, encoding='utf-8')

                    elif ext in [".bat", ".cmd"]:
                        res = subprocess.run(local_path, shell=True, capture_output=True, text=True, encoding='utf-8')

                    elif ext == ".exe":
                        res = subprocess.run(local_path, shell=True, capture_output=True, text=True, encoding='utf-8')

                    else:
                        res = subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Wrong script type.")
                else:
                    res = subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Wrong command format.")

            else:
                # Якщо це не завантаження скрипта, виконуємо напряму
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

            # Надсилання результату на сервер
            requests.post(f"{url}/agent_post_result/{sid}", json={
                "stdout": res.stdout,
                "stderr": res.stderr,
                "code": res.returncode
            })

    except Exception as e:
        # Для відлагодження можна записати у файл:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}\n")

    time.sleep(3)
