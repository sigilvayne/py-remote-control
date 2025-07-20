import os
import time
import json
import subprocess
import requests
import uuid
import shutil

CONFIG_PATH = "C:/Script/agent/config.json"
SCRIPT_DIR = "C:/Script/agent/tmp"
POLL_INTERVAL = 2  # seconds

os.makedirs(SCRIPT_DIR, exist_ok=True)

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def download_script(script_url, filename):
    local_path = os.path.join(SCRIPT_DIR, filename)
    try:
        r = requests.get(script_url)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        return local_path
    except Exception as e:
        return None

def run_command(command):
    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8'
        )
        return {
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def execute(payload, control_center_url, server_id):
    command = payload.get("command", "")
    cmd_id = payload.get("id", str(uuid.uuid4()))

    result = {
        "id": cmd_id,
        "stdout": "",
        "stderr": "",
        "returncode": -1
    }

    try:
        if command.endswith(".ps1"):
            script_url = f"{control_center_url}/scripts/{command}"
            script_path = download_script(script_url, command)
            if not script_path:
                result["stderr"] = f"Не вдалося завантажити скрипт: {command}"
            else:
                ps_cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{script_path}"'
                result.update(run_command(ps_cmd))

        elif command.endswith(".exe"):
            exe_path = os.path.join(SCRIPT_DIR, command)
            if not os.path.exists(exe_path):
                exe_url = f"{control_center_url}/scripts/{command}"
                exe_path = download_script(exe_url, command)
            result.update(run_command(f'"{exe_path}"'))

        else:
            # CMD-команда
            result.update(run_command(command))

    except Exception as e:
        result["stderr"] = str(e)

    # Відправити результат назад
    try:
        r = requests.post(f"{control_center_url}/agent_post_result/{server_id}", json=result)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Помилка надсилання результату: {e}")

def main():
    config = load_config()
    server_id = config["server_id"]
    control_center_url = config["control_center_url"].rstrip('/')

    print(f"[✓] Агент запущено для сервера: {server_id}")

    while True:
        try:
            r = requests.get(f"{control_center_url}/agent_get_command/{server_id}")
            r.raise_for_status()
            data = r.json()
            if data.get("command"):
                print(f"[→] Отримано команду: {data['command']}")
                execute(data, control_center_url, server_id)
            else:
                print("[•] Немає нових команд")
        except Exception as e:
            print(f"[!] Помилка під час перевірки команди: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
