import time
import requests
import subprocess
import json
import os
import threading
import uuid
import shutil

# Завантаження конфігурації
cfg = json.load(open("C:/Script/agent/config.json"))
sid = cfg["server_id"]
url = cfg["control_center_url"]

SCRIPT_DIR = "C:/Script/agent/tmp"
os.makedirs(SCRIPT_DIR, exist_ok=True)

# Лічильник невдалих перевірок
no_command_counter = 0
MAX_EMPTY_POLLS = 10  # після 10 перевірок без команди — очищення

def clear_tmp_folder():
    for filename in os.listdir(SCRIPT_DIR):
        file_path = os.path.join(SCRIPT_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            with open("agent_error.log", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error deleting {file_path}: {str(e)}\n")


def run_command(command: str):
    try:
        if command.startswith("download_and_run_script"):
            parts = command.strip().split(maxsplit=2)
            if len(parts) >= 2:
                script_name = parts[1]
                script_args = parts[2] if len(parts) > 2 else ""
                script_url = f"{url}/scripts/{script_name}"
                local_path = os.path.join(SCRIPT_DIR, script_name)

                # Завантаження скрипта
                script_res = requests.get(script_url)
                with open(local_path, "wb") as f:
                    f.write(script_res.content)

                ext = os.path.splitext(script_name)[1].lower()

                if ext == ".ps1":
                    res = subprocess.run([
                        "powershell",
                        "-ExecutionPolicy", "Bypass",
                        "-Command",
                        f"$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8; & '{local_path}' {script_args}"
                    ], capture_output=True, text=True, encoding='utf-8')

                elif ext in [".bat", ".cmd", ".exe"]:
                    full_cmd = f'"{local_path}" {script_args}'
                    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

                else:
                    res = subprocess.CompletedProcess(args=command, returncode=1, stdout="", stderr="Wrong script type.")
            else:
                res = subprocess.CompletedProcess(args=command, returncode=1, stdout="", stderr="Wrong command format.")

        else:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')

        # Надсилання результату на сервер
        requests.post(f"{url}/agent_post_result/{sid}", json={
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode
        })

    except Exception as e:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in thread: {str(e)}\n")


while True:
    try:
        r = requests.get(f"{url}/agent_get_command/{sid}")
        r.raise_for_status()
        cmd = r.json().get("command")

        if cmd:
            no_command_counter = 0  # скидаємо лічильник
            thread = threading.Thread(target=run_command, args=(cmd,))
            thread.start()
        else:
            no_command_counter += 1
            if no_command_counter >= MAX_EMPTY_POLLS:
                clear_tmp_folder()
                no_command_counter = 0  # скинути після очищення

    except Exception as e:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Main loop error: {str(e)}\n")

    time.sleep(3)
