import time
import requests
import subprocess
import json
import os
import threading
import shutil

# Config load
cfg = json.load(open("C:/Script/agent/config.json"))
sid = cfg["server_id"]
url = cfg["control_center_url"]
agent_token = cfg.get("agent_token") 

SCRIPT_DIR = "C:/Script/agent/tmp"
os.makedirs(SCRIPT_DIR, exist_ok=True)

no_command_counter = 0
MAX_EMPTY_POLLS = 10

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

def send_progress_update(command_id, output_chunk="", is_complete=False, stderr="", code=0):
    """Send progress update to the server"""
    try:
        progress_url = f"{url}/agent_post_progress/{sid}?token={agent_token}"
        progress_data = {
            "id": command_id,
            "output": output_chunk,
            "complete": is_complete,
            "stderr": stderr,
            "code": code
        }
        requests.post(progress_url, json=progress_data)
    except Exception as e:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error sending progress: {str(e)}\n")

def run_complex_command(command_id, command):
    """Run complex command with progress updates"""
    try:
        if command.startswith("download_and_run_script"):
            parts = command.strip().split(maxsplit=2)
            if len(parts) >= 2:
                script_name = parts[1]
                script_args = parts[2] if len(parts) > 2 else ""
                script_url = f"{url}/scripts/{script_name}?token={agent_token}"
                local_path = os.path.join(SCRIPT_DIR, script_name)

                # Send initial progress
                send_progress_update(command_id, "Завантаження скрипту...\n")

                script_res = requests.get(script_url)
                script_res.raise_for_status()
                
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(script_res.content)

                send_progress_update(command_id, "Скрипт завантажено. Запуск...\n")

                ext = os.path.splitext(script_name)[1].lower()
                output_buffer = ""
                last_send_time = time.time()

                if ext == ".ps1":
                    process = subprocess.Popen([
                        "powershell",
                        "-ExecutionPolicy", "Bypass",
                        "-Command",
                        f"$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8; & '{local_path}' {script_args}"
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', bufsize=1, universal_newlines=True)

                    # Read output in real-time
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            output_buffer += output
                            # Send progress every 5 seconds or when buffer gets large
                            current_time = time.time()
                            if current_time - last_send_time >= 5 or len(output_buffer) > 1000:
                                send_progress_update(command_id, output_buffer)
                                output_buffer = ""
                                last_send_time = current_time

                    # Get any remaining output and stderr
                    remaining_output, stderr_output = process.communicate()
                    if remaining_output:
                        output_buffer += remaining_output
                    
                    if output_buffer:
                        send_progress_update(command_id, output_buffer)
                    
                    # Send final result
                    send_progress_update(command_id, "", True, stderr_output, process.returncode)

                elif ext in [".bat", ".cmd", ".exe"]:
                    process = subprocess.Popen(
                        f'"{local_path}" {script_args}',
                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                        text=True, encoding='utf-8', bufsize=1, universal_newlines=True
                    )

                    # Read output in real-time
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            output_buffer += output
                            # Send progress every 5 seconds or when buffer gets large
                            current_time = time.time()
                            if current_time - last_send_time >= 5 or len(output_buffer) > 1000:
                                send_progress_update(command_id, output_buffer)
                                output_buffer = ""
                                last_send_time = current_time

                    # Get any remaining output and stderr
                    remaining_output, stderr_output = process.communicate()
                    if remaining_output:
                        output_buffer += remaining_output
                    
                    if output_buffer:
                        send_progress_update(command_id, output_buffer)
                    
                    # Send final result
                    send_progress_update(command_id, "", True, stderr_output, process.returncode)

                else:
                    send_progress_update(command_id, "Непідтримуваний тип скрипту.\n", True, "Wrong script type.", 1)
            else:
                send_progress_update(command_id, "Неправильний формат команди.\n", True, "Wrong command format.", 1)
        else:
            # For non-script commands, run normally and send progress
            send_progress_update(command_id, "Виконання команди...\n")
            
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', bufsize=1, universal_newlines=True
            )

            output_buffer = ""
            last_send_time = time.time()

            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_buffer += output
                    # Send progress every 5 seconds or when buffer gets large
                    current_time = time.time()
                    if current_time - last_send_time >= 5 or len(output_buffer) > 1000:
                        send_progress_update(command_id, output_buffer)
                        output_buffer = ""
                        last_send_time = current_time

            # Get any remaining output and stderr
            remaining_output, stderr_output = process.communicate()
            if remaining_output:
                output_buffer += remaining_output
            
            if output_buffer:
                send_progress_update(command_id, output_buffer)
            
            # Send final result
            send_progress_update(command_id, "", True, stderr_output, process.returncode)

    except Exception as e:
        error_msg = f"Помилка виконання команди: {str(e)}"
        send_progress_update(command_id, error_msg, True, str(e), 1)

def run_command(command_id: str, command: str):
    try:
        # Check if this is a complex command (update scripts)
        is_complex = any(script in command for script in [
            "search-updates.ps1", "run-update.ps1", "disk-cleanup.ps1", 
            "dism-cleanup.ps1", "dism-analyze.ps1", "dism-health.ps1"
        ])
        
        if is_complex:
            # Run complex command with progress updates
            run_complex_command(command_id, command)
        else:
            # Run simple command normally
            if command.startswith("download_and_run_script"):
                parts = command.strip().split(maxsplit=2)
                if len(parts) >= 2:
                    script_name = parts[1]
                    script_args = parts[2] if len(parts) > 2 else ""
                    script_url = f"{url}/scripts/{script_name}?token={agent_token}"
                    local_path = os.path.join(SCRIPT_DIR, script_name)

                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    script_res = requests.get(script_url)
                    script_res.raise_for_status()
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

            post_url = f"{url}/agent_post_result/{sid}?token={agent_token}"
            requests.post(post_url, json={
                "id": command_id,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "code": res.returncode
            })

    except Exception as e:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in thread: {str(e)}\n")

while True:
    try:
        get_url = f"{url}/agent_get_command/{sid}?token={agent_token}"
        r = requests.get(get_url)
        r.raise_for_status()
        data = r.json()

        command = data.get("command")
        command_id = data.get("id")

        if command and command_id:
            no_command_counter = 0 
            thread = threading.Thread(target=run_command, args=(command_id, command))
            thread.start()
        else:
            no_command_counter += 1
            if no_command_counter >= MAX_EMPTY_POLLS:
                clear_tmp_folder()
                no_command_counter = 0

    except Exception as e:
        with open("agent_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Main loop error: {str(e)}\n")

    time.sleep(3)
